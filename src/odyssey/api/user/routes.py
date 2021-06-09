from datetime import datetime, timedelta
import boto3
import jwt

from flask import current_app, request, jsonify, redirect
from flask_accepts import accepts, responds
from flask_restx import Resource
from werkzeug.security import check_password_hash


from odyssey.api import api
from odyssey.api.client.schemas import ClientInfoSchema, ClientGeneralMobileSettingsSchema, ClientRaceAndEthnicitySchema
from odyssey.api.client.models import ClientClinicalCareTeam
from odyssey.api.lookup.models import LookupSubscriptions, LookupLegalDocs
from odyssey.api.staff.schemas import StaffProfileSchema, StaffRolesSchema
from odyssey.api.user.models import (
    User,
    UserLogin,
    UserRemovalRequests,
    UserSubscriptions,
    UserTokenHistory,
    UserTokensBlacklist,
    UserPendingEmailVerifications,
    UserLegalDocs
)
from odyssey.api.staff.models import StaffRoles
from odyssey.api.user.schemas import (
    UserSchema, 
    UserLoginSchema,
    UserPasswordRecoveryContactSchema,
    UserPasswordResetSchema,
    UserPasswordUpdateSchema,
    NewClientUserSchema,
    UserInfoSchema,
    UserSubscriptionsSchema,
    UserSubscriptionHistorySchema,
    NewStaffUserSchema,
    UserLegalDocsSchema
)

from odyssey.utils.auth import token_auth, basic_auth
from odyssey.utils.constants import PASSWORD_RESET_URL, DB_SERVER_TIME
from odyssey.utils.errors import (
    InputError,
    StaffEmailInUse,
    ClientEmailInUse,
    UnauthorizedUser,
    GenericNotFound,
    InvalidVerificationCode,
    IllegalSetting
)
from odyssey.utils.message import send_email_password_reset, send_email_delete_account, send_email_verify_email
from odyssey.utils.misc import check_user_existence, check_client_existence, check_staff_existence, verify_jwt
from odyssey.utils import search
from odyssey import db

ns = api.namespace('user', description='Endpoints for user accounts.')


@ns.route('/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ApiUser(Resource):
    
    @token_auth.login_required
    @responds(schema=UserSchema, api=ns)
    def get(self, user_id):
        check_user_existence(user_id)

        return User.query.filter_by(user_id=user_id).one_or_none()

    @token_auth.login_required
    def delete(self, user_id):
        #Search for user by user_id in User table
        check_user_existence(user_id)
        user = User.query.filter_by(user_id=user_id).one_or_none()
        requester = token_auth.current_user()[0]
        removal_request = UserRemovalRequests(
            requester_user_id=requester.user_id, 
            user_id=user.user_id)

        db.session.add(removal_request)
        db.session.flush()
        
        #Get a list of all tables in database
        tableList = db.session.execute("SELECT distinct(table_name) from information_schema.columns\
                WHERE column_name='user_id';").fetchall()
        
        #Send notification email to user being deleted and user requesting deletion
        #when FLASK_ENV=production
        if user.email != requester.email:
            send_email_delete_account(requester.email, user.email)
        send_email_delete_account(user.email, user.email)

        #when user is staff
        #keep name, email, modobio id, user id in User table
        #keep lines in tables where user_id is the reporter_id
        if user.is_client and not user.is_staff:
            #keep only modobio id, user id in User table
            user.email = None
            user.firstname = None
            user.middlename = None
            user.lastname = None
        user.phone_number = None
        user.deleted = True
        
        #delete files or images saved in S3 bucket for user_id
        s3 = boto3.client('s3')

        bucket_name = current_app.config['S3_BUCKET_NAME']
        user_directory=f'id{user_id:05d}/'

        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=user_directory)

        for object in response.get('Contents', []):
            print('Deleting', object['Key'])
            s3.delete_object(Bucket=bucket_name, Key=object['Key'])
        
        #delete lines with user_id in all other tables except "User" and "UserRemovalRequests"
        for table in tableList:
            tblname = table.table_name
            #added data_per_client table due to issues with the testing database
            if tblname != "User" and tblname != "UserRemovalRequests" and tblname != "data_per_client":
                db.session.execute("DELETE FROM \"{}\" WHERE user_id={};".format(tblname, user_id))

        db.session.commit()

        #remove user from elastic search indices (must be done after commit)
        search.delete_from_index(user.user_id)

        return {'message': f'User with id {user_id} has been removed'}

@ns.route('/staff/')
class NewStaffUser(Resource):
    @token_auth.login_required
    @accepts(schema=NewStaffUserSchema, api=ns)
    @responds(schema=NewStaffUserSchema, status_code=201, api=ns)
    def post(self):
        """
        Create a staff user. Payload will require userinfo and staffinfo
        sections. Currently, staffinfo is used to register the staff user with 
        one or more access_roles. 

        If registering an already existing CLIENT user as a STAFF user, 
        the password must match, or be and empty string (ie. "")
        """
        data = request.get_json()
        
        # Check if user exists already
        user_info = data.get('user_info')
        #input email made to lowercase to prevet future issues with authentication
        user_info['email'] = user_info.get('email').lower()
        staff_info = data.get('staff_info')

        user = User.query.filter(User.email.ilike(user_info.get('email'))).first()
        if user:
            if user.is_staff:
                # user account already exists for this email and is already a staff account
                raise StaffEmailInUse(email=user_info.get('email'))
            else:
                #user account exists but only the client portion of the account is defined
                user.is_staff = True
                staff_profile = StaffProfileSchema().load({'user_id': user.user_id})
                db.session.add(staff_profile)

                # add new staff subscription information
                staff_sub = UserSubscriptionsSchema().load({
                    'subscription_type_id': 2,
                    'subscription_status': 'subscribed',
                    'is_staff': True
                })
                staff_sub.user_id = user.user_id
                db.session.add(staff_sub)
        else:
            # user account does not yet exist for this email
            # require password
            password = user_info.get('password', None)
            if not password:
                raise InputError(status_code=400,message='password required')
            del user_info['password']
            
            user_info["is_client"] = False
            user_info["is_staff"] = True
            # create entry into User table first
            # use the generated user_id for UserLogin & StaffProfile tables
            user = UserSchema().load(user_info)
            db.session.add(user) 
            db.session.flush()

            user_login = UserLoginSchema().load({"user_id": user.user_id, "password": password})
            staff_profile = StaffProfileSchema().load({"user_id": user.user_id})
            db.session.add(user_login)
            db.session.add(staff_profile)

            # add new user subscription information
            staff_sub = UserSubscriptionsSchema().load({
                'subscription_type_id': 2,
                'subscription_status': 'subscribed',
                'is_staff': True
            })
            staff_sub.user_id = user.user_id
            db.session.add(staff_sub)

            # generate token and code for email verifciation
            token = UserPendingEmailVerifications.generate_token(user.user_id)
            code = UserPendingEmailVerifications.generate_code()

            # create pending email verification in db
            email_verification_data = {
                'user_id': user.user_id,
                'token': token,
                'code': code
            }

            verification = UserPendingEmailVerifications(**email_verification_data)
            db.session.add(verification)

            # send email to the user
            send_email_verify_email(user, token, code)
        
        # create entries for role assignments 
        for role in staff_info.get('access_roles', []):
            db.session.add(StaffRolesSchema().load(
                                            {'user_id': user.user_id,
                                             'role': role}
                                            ))

        db.session.commit()
        db.session.refresh(user)
        payload = user.__dict__
        payload["staff_info"] = {"access_roles": staff_info.get('access_roles', []), 
                                "access_roles_v2": StaffRoles.query.filter_by(user_id = user.user_id)}
    
        payload["user_info"] =  user
        return payload


@ns.route('/staff/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class StaffUserInfo(Resource):
    @token_auth.login_required
    @responds(schema=NewStaffUserSchema, status_code=200, api=ns)
    def get(self, user_id):
        user = User.query.filter_by(user_id=user_id).one_or_none()
        staff_roles = StaffRoles.query.filter_by(user_id = user.user_id)

        access_roles = []
        for role in staff_roles:
            access_roles.append(role.role)

        payload = {
                    "staff_info": 
                        {
                            "access_roles": access_roles,
                            "access_roles_v2": staff_roles
                        },
                    "user_info": 
                        user}
        return payload

@ns.route('/client/')
class NewClientUser(Resource):
    @accepts(schema=UserInfoSchema, api=ns)
    @responds(schema=NewClientUserSchema, status_code=201, api=ns)
    def post(self): 
        """
        Create a client user. This endpoint requires a payload with just userinfo.
        
        If registering an already existing staff user as a client, 
        the password provided must match the one already in use by staff account
        """

        user_info = request.get_json()     
        user_info['email'] = user_info.get('email').lower()
        user = User.query.filter(User.email.ilike(user_info.get('email'))).first()
        if user:
            if user.is_client:
                # user account already exists for this email and is already a client account
                raise ClientEmailInUse(email=user_info.get('email'))
            else:
                # user account exists but only the staff portion of the account is defined
                #verify password matches already existing staff login info before allowing client access
                password= user_info.get('password')
                del user_info['password']
                user, user_login, _ = basic_auth.verify_password(username=user.email, password=password)
                
                #Create client account for existing staff member
                user.is_client = True
                client_info = ClientInfoSchema().load({'user_id': user.user_id})
                
                db.session.add(client_info)
        else:
            # user account does not yet exist for this email
            password=user_info.get('password', None)
            if not password:
                raise InputError(status_code=400,message='password required')
            del user_info['password']
            user_info['is_client'] = True
            user_info['is_staff'] = False
            user = UserSchema().load(user_info)
            db.session.add(user)
            db.session.flush()
            user_login = UserLoginSchema().load({"user_id": user.user_id, "password": password})
            client_info = ClientInfoSchema().load({"user_id": user.user_id})
            db.session.add(client_info)
            db.session.add(user_login)

            # generate token and code for email verification
            token = UserPendingEmailVerifications.generate_token(user.user_id)
            code = UserPendingEmailVerifications.generate_code()

            # create pending email verification in db
            email_verification_data = {
                'user_id': user.user_id,
                'token': token,
                'code': code
            }

            verification = UserPendingEmailVerifications(**email_verification_data)
            db.session.add(verification)

            # send email to the user
            send_email_verify_email(user, token, code)

            #Authenticate newly created client accnt for immediate login
            user, user_login, _ = basic_auth.verify_password(username=user.email, password=password)

        # add new client subscription information
        client_sub = UserSubscriptionsSchema().load({
            'subscription_status': 'unsubscribed',
            'subscription_type_id': 1,
            'is_staff': False
        })
        client_sub.user_id = user.user_id
        db.session.add(client_sub)

        # add default client mobile settings
        client_mobile_settings = ClientGeneralMobileSettingsSchema().load({
            "include_timezone": True,
            "display_middle_name": False,
            "use_24_hour_clock": False,
            "is_right_handed": True,
            "enable_push_notifications": False,
            "timezone_tracking": False,
            "biometrics_setup": False,
            "date_format": "%d-%b-%Y"
        })
        client_mobile_settings.user_id = user.user_id
        db.session.add(client_mobile_settings)

        # add default client race and ethnicity settings
        client_mother_race_info = ClientRaceAndEthnicitySchema().load({'is_client_mother': True, 'race_id': 1})
        client_mother_race_info.user_id = user.user_id
        client_father_race_info = ClientRaceAndEthnicitySchema().load({'is_client_mother': False, 'race_id': 1})
        client_father_race_info.user_id = user.user_id
        db.session.add(client_mother_race_info)
        db.session.add(client_father_race_info)     

        #Generate access and refresh tokens
        access_token = UserLogin.generate_token(user_type='client', user_id=user.user_id, token_type='access')
        refresh_token = UserLogin.generate_token(user_type='client', user_id=user.user_id, token_type='refresh')
        
        #Add refresh token to db
        db.session.add(UserTokenHistory(user_id=user.user_id, 
                                        refresh_token=refresh_token,
                                        event='login',
                                        ua_string = request.headers.get('User-Agent')))

        db.session.commit()

        payload = {'user_info': user, 'token':access_token, 'refresh_token':refresh_token}
        return payload

@ns.route('/password/forgot-password/recovery-link/')
class PasswordResetEmail(Resource):
    """Password reset endpoints."""
    
    @accepts(schema=UserPasswordRecoveryContactSchema, api=ns)
    def post(self):
        """begin a password reset session. 
            Staff member unable to log in will request a password reset
            with only their email. Emails will be checked for exact match in the database
            to a staff member. 
    
            If the email exists, a signed JWT is created; encoding the token's expiration 
            time and the user_id. The code will be placed into this URL <url for password reset>
            and sent to a valid email address.  
            If the email does not exist, no email is sent. 
            response 200 OK
        """
        email = request.parsed_obj['email']

        user = User.query.filter_by(email=email.lower()).first()
        
        if not email or not user:
            return 200

        secret = current_app.config['SECRET_KEY']
        password_reset_token = jwt.encode({'exp': datetime.utcnow()+timedelta(minutes = 15), 
                                  'sid': user.user_id}, 
                                  secret, 
                                  algorithm='HS256')
                                  
        send_email_password_reset(user.email, password_reset_token)

        # DEV mode won't send an email, so return password. DEV mode ONLY.
        if current_app.config['DEV']:
            return jsonify({"token": password_reset_token,
                            "password_reset_url" : PASSWORD_RESET_URL.format(password_reset_token)})

        return 200
        

@ns.route('/password/forgot-password/reset')
@ns.doc(params={'reset_token': "token from password reset endpoint"})
class ResetPassword(Resource):
    """Reset the user's password."""

    @accepts(schema=UserPasswordResetSchema, api=ns)
    def put(self):
        """
            Change the current password to the one given
            in the body of this request
            response 200 OK
       """
        # decode and validate token 
        secret = current_app.config['SECRET_KEY']
        reset_token=request.args.get("reset_token")
        try:
            decoded_token = jwt.decode(reset_token, secret, algorithms='HS256')
        except jwt.ExpiredSignatureError:
            raise UnauthorizedUser(message="Token authorization expired")

        # bring up the staff member and reset their password
        pswd = request.parsed_obj['password']

        user = UserLogin.query.filter_by(user_id=decoded_token['sid']).first()
        user.set_password(pswd)

        db.session.commit()

        return 200

@ns.route('/password/update/')
class ChangePassword(Resource):
    """Reset the user's password."""
    @token_auth.login_required
    @accepts(schema=UserPasswordUpdateSchema, api=ns)
    def post(self):
        """
            Change the current password to the one given
            in the body of this request
            response 200 OK
        """
        # bring up the staff member and reset their password
        _, user_login = token_auth.current_user()

        if check_password_hash(user_login.password, request.parsed_obj['current_password']):
            user_login.set_password(request.parsed_obj['new_password'])
        else:
            raise UnauthorizedUser(message="please enter the correct current password \
                                      otherwise, visit the password recovery endpoint \
                                      /staff/password/forgot-password/recovery-link")
        db.session.commit()

        return 200

@ns.route('/token/refresh')
@ns.doc(params={'refresh_token': "token from password reset endpoint"})
class RefreshToken(Resource):
    """User refesh token to issue a new token with a 1 hr TTL"""
    def post(self):
        """
        Issues new API access token if refrsh_token is still valid
        """
        refresh_token = request.args.get("refresh_token")
        
        # ensure refresh token is not on blacklist
        if UserTokensBlacklist.query.filter_by(token=refresh_token).one_or_none():
            # log failed refresh attempt
            token_payload = jwt.decode(refresh_token, options={'verify_signature': False})
            db.session.add(UserTokenHistory(user_id=token_payload.get('uid'), 
                                        event='refresh',
                                        ua_string = request.headers.get('User-Agent')))
            db.session.commit()
            raise InputError(message="invalid token", status_code=401)

        # check that the token is valid
        decoded_token = verify_jwt(refresh_token, refresh=True)
        
        # if valid, create a new access token, return it in the payload
        access_token = UserLogin.generate_token(user_id=decoded_token['uid'], user_type=decoded_token['utype'], token_type='access')
        new_refresh_token = UserLogin.generate_token(user_id=decoded_token['uid'], user_type=decoded_token['utype'], token_type='refresh')  
        
        # add refresh details to UserTokenHistory table
        db.session.add(UserTokenHistory(user_id=decoded_token['uid'], 
                                        refresh_token=new_refresh_token,
                                        event='refresh',
                                        ua_string = request.headers.get('User-Agent')))


        # add old refresh token to blacklist
        db.session.add(UserTokensBlacklist(token=refresh_token))
        db.session.commit()

        return {'access_token': access_token,
                'refresh_token': new_refresh_token}, 201

@ns.route('/registration-portal/verify')
@ns.doc(params={'portal_id': "registration portal id"})
class VerifyPortalId(Resource):
    """
    Verify registration portal id and update user type
    
    New users registered by client services must first go through this endpoint in 
    order to access any other resource. This API completes the user's registration
    so they may then request an API token. 
    
    """
    def put(self):
        """
        check token validity
        bring up user
        update user type (client or staff)
        """
        portal_id = request.args.get("portal_id")

        decoded_token = verify_jwt(portal_id)

        user = User.query.filter_by(user_id=decoded_token['uid']).one_or_none()
        
        if not user:
            raise UnauthorizedUser

        if decoded_token['utype'] == 'client':
            user.is_client = True
            client_info = ClientInfoSchema().load({'user_id': user.user_id})
            db.session.add(client_info)
        elif decoded_token['utype'] == 'staff':
            user.is_staff = True

        # mark user email as verified        
        user.email_verified = True
        db.session.commit()
        
        return 200

@ns.route('/subscription/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class UserSubscriptionApi(Resource):

    @token_auth.login_required
    @responds(schema=UserSubscriptionsSchema(many=True), api=ns, status_code=200)
    def get(self, user_id):
        """
        Returns active subscription information for the given user_id. 
        Because a user_id can belong to both a client and staff account, both active subscriptions will be returned in this case.
        """
        check_user_existence(user_id)

        return UserSubscriptions.query.filter_by(user_id=user_id).filter_by(end_date=None).all()

    @token_auth.login_required
    @accepts(schema=UserSubscriptionsSchema, api=ns)
    @responds(schema=UserSubscriptionsSchema, api=ns, status_code=201)
    def put(self, user_id):
        """
        Updates the currently active subscription for the given user_id. 
        Also sets the end date to the previously active subscription.
        """
        if request.parsed_obj.is_staff:
            check_staff_existence(user_id)
        else:
            check_client_existence(user_id)
        
        new_sub_info =  LookupSubscriptions.query.filter_by(sub_id=request.parsed_obj.subscription_type_id).one_or_none()
            
        if not new_sub_info:
            raise InputError(400, 'Invalid subscription_type_id.')

        #update end_date for user's previous subscription
        #NOTE: users always have a subscription, even a brand new account will have an entry
        #      in this table as an 'unsubscribed' subscription
        prev_sub = UserSubscriptions.query.filter_by(user_id=user_id, end_date=None, is_staff=request.parsed_obj.is_staff).one_or_none()
        prev_sub.update({'end_date': DB_SERVER_TIME})

        new_data = {
            'subscription_status': request.parsed_obj.subscription_status,
            'subscription_type_id': request.parsed_obj.subscription_type_id,
            'is_staff': request.parsed_obj.is_staff,
        }

        new_sub = UserSubscriptionsSchema().load(new_data)
        new_sub.user_id = user_id
        
        db.session.add(new_sub)
        db.session.commit()

        new_sub.subscription_type_information = new_sub_info
        return new_sub

    

@ns.route('/subscription/history/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class UserSubscriptionHistoryApi(Resource):

    @token_auth.login_required
    @responds(schema=UserSubscriptionHistorySchema, api=ns, status_code=200)
    def get(self, user_id):
        """
        Returns the complete subscription history for the given user_id.
        Because a user_id can belong to both a client and staff account, both subscription histories will be returned in this case.
        """
        check_user_existence(user_id)

        client_history = UserSubscriptions.query.filter_by(user_id=user_id).filter_by(is_staff=False).all()
        staff_history = UserSubscriptions.query.filter_by(user_id=user_id).filter_by(is_staff=True).all()

        for sub in client_history:
            sub.subscription_type_information = LookupSubscriptions.query.filter_by(sub_id=sub.subscription_type_id).one_or_none()

        for sub in staff_history:
            sub.subscription_type_information = LookupSubscriptions.query.filter_by(sub_id=sub.subscription_type_id).one_or_none()


        res = {}
        res['client_subscription_history'] = client_history
        res['staff_subscription_history'] = staff_history
        return res

@ns.route('/logout/')
class UserLogoutApi(Resource):

    @token_auth.login_required
    def post(self):
        """
        Places the user's current set of tokens on the token blacklist.
        The user will have to login with a username and password to regain access.
        """
        refresh_token = token_auth.current_user()[1].refresh_token
        
        #remove 'Bearer ' from the front of the access token
        access_token = request.headers.get('Authorization').split()[1]

        db.session.add(UserTokensBlacklist(token=refresh_token))
        db.session.add(UserTokensBlacklist(token=access_token))
        db.session.commit()

        return 200

        res = []
        for client in ClientClinicalCareTeam.query.filter_by(team_member_user_id=user_id).all():
            user = User.query.filter_by(user_id=client.user_id).one_or_none()
            res.append({'client_user_id': user.user_id, 
                        'client_name': ''.join(filter(None, (user.firstname, user.middlename ,user.lastname))),
                        'client_email': user.email})
        
        return res


# TODO: remove these redirects once fixed on frontend

from odyssey.api.notifications.schemas import NotificationSchema

@ns.route('/notifications/<int:user_id>/')
@ns.deprecated
@ns.doc(params={'user_id': 'User ID number'})
class UserNotificationsApi(Resource):
    @token_auth.login_required
    @responds(
        api=ns,
        status_code=308,
        description='Permanently moved to GET /notifications/<user_id>/')
    def get(self, user_id):
        """ [DEPRECATED] Moved to GET `/notifications/<user_id>/`. """
        return redirect(f'/notifications/{user_id}/', code=308)


@ns.route('/notifications/<int:idx>/')
@ns.deprecated
@ns.doc(params={'idx': 'Notification idx number'})
class UserNotificationsPutApi(Resource):
    @token_auth.login_required
    @accepts(schema=NotificationSchema, api=ns)
    @responds(
        api=ns,
        status_code=308,
        description='Permanently moved to PUT /notifications/<notification_id>/')
    def put(self, idx):
        """ [DEPRECATED] Moved to PUT `/notifications/<notification_id>/`. """
        return redirect(f'/notifications/{idx}/', code=308)


@ns.route('/email-verification/token/<string:token>/')
@ns.doc(params={'token': 'Email verification token'})
class UserPendingEmailVerificationsTokenApi(Resource):

    @responds(status_code=200)
    def get(self, token):
        """
        Checks if token has not expired and exists in db.
        If true, removes pending verification object and returns 200.
        """
        # decode and validate token 
        secret = current_app.config['SECRET_KEY']

        try:
            decoded_token = jwt.decode(token, secret, algorithms='HS256')
        except jwt.ExpiredSignatureError:
            raise UnauthorizedUser(message="Token authorization expired")

        verification = UserPendingEmailVerifications.query.filter_by(token=token).one_or_none()

        if not verification:
            raise UnauthorizedUser(message="Invalid email verification token authorization")

        #token was valid, remove the pending request, update user account and return 200
        user = User.query.filter_by(user_id=verification.user_id).one_or_none()
        user.update({'email_verified': True})
        
        db.session.delete(verification)
        db.session.commit()
        

@ns.route('/email-verification/code/<int:user_id>/')
@ns.doc(params={'code': 'Email verification code'})
class UserPendingEmailVerificationsCodeApi(Resource):

    @responds(status_code=200)
    def post(self, user_id):

        verification = UserPendingEmailVerifications.query.filter_by(user_id=user_id).one_or_none()

        if not verification:
            raise GenericNotFound("There is no pending email verification for user ID " + str(user_id))

        if verification.code != request.args.get('code'):
            raise InvalidVerificationCode

        # Decode and validate token. Code should expire the same time the token does.
        secret = current_app.config['SECRET_KEY']

        try:
            decoded_token = jwt.decode(verification.token, secret, algorithms='HS256')
        except jwt.ExpiredSignatureError:
            raise UnauthorizedUser(message="Code has expired")

        #code was valid, remove the pending request, update user account and return 200
        db.session.delete(verification)

        user = User.query.filter_by(user_id=user_id).one_or_none()
        user.update({'email_verified': True})

        db.session.commit()

@ns.route('/email-verification/resend/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class UserPendingEmailVerificationsResendApi(Resource):
    """
    If a user waited too long to verify their email and their token/code have expired,
    they can use this endpoint to create another token/code and send another email. This 
    can also be used if the user never received an email.
    """

    @responds(status_code=200)
    def post(self, user_id):
        verification = UserPendingEmailVerifications.query.filter_by(user_id=user_id).one_or_none()
            
        if not verification:
            raise GenericNotFound("There is no pending email verification for user ID " + str(user_id))

        # create a new token and code for this user
        token = UserPendingEmailVerifications.generate_token(user_id)
        code = UserPendingEmailVerifications.generate_code()

        verification.update(
            {
                'token': token,
                'code': code
            }
        )

        db.session.commit()

        recipient = User.query.filter_by(user_id=user_id).one_or_none()

        send_email_verify_email(recipient, token, code)

@ns.route('/email-verification/token/<string:token>/')
@ns.doc(params={'token': 'Email verification token'})
class UserPendingEmailVerificationsTokenApi(Resource):

    @responds(status_code=200)
    def get(self, token):
        """
        Checks if token has not expired and exists in db.
        If true, removes pending verification object and returns 200.
        """
        # decode and validate token 
        secret = current_app.config['SECRET_KEY']

        try:
            decoded_token = jwt.decode(token, secret, algorithms='HS256')
        except jwt.ExpiredSignatureError:
            raise UnauthorizedUser(message="Token authorization expired")

        verification = UserPendingEmailVerifications.query.filter_by(token=token).one_or_none()

        if not verification:
            raise UnauthorizedUser(message="Invalid email verification token authorization")

        #token was valid, remove the pending request, update user account and return 200
        user = User.query.filter_by(user_id=verification.user_id).one_or_none()
        user.update({'email_verified': True})
        
        db.session.delete(verification)
        db.session.commit()
        

@ns.route('/email-verification/code/<int:user_id>/')
@ns.doc(params={'code': 'Email verification code'})
class UserPendingEmailVerificationsCodeApi(Resource):

    @responds(status_code=200)
    def post(self, user_id):

        verification = UserPendingEmailVerifications.query.filter_by(user_id=user_id).one_or_none()

        if not verification:
            raise GenericNotFound("There is no pending email verification for user ID " + str(user_id))

        if verification.code != request.args.get('code'):
            raise InvalidVerificationCode

        # Decode and validate token. Code should expire the same time the token does.
        secret = current_app.config['SECRET_KEY']

        try:
            decoded_token = jwt.decode(verification.token, secret, algorithms='HS256')
        except jwt.ExpiredSignatureError:
            raise UnauthorizedUser(message="Code has expired")

        #code was valid, remove the pending request, update user account and return 200
        db.session.delete(verification)

        user = User.query.filter_by(user_id=user_id).one_or_none()
        user.update({'email_verified': True})

        db.session.commit()

@ns.route('/email-verification/resend/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class UserPendingEmailVerificationsResendApi(Resource):
    """
    If a user waited too long to verify their email and their token/code have expired,
    they can use this endpoint to create another token/code and send another email. This 
    can also be used if the user never received an email.
    """

    @responds(status_code=200)
    def post(self, user_id):
        verification = UserPendingEmailVerifications.query.filter_by(user_id=user_id).one_or_none()
            
        if not verification:
            raise GenericNotFound("There is no pending email verification for user ID " + str(user_id))

        # create a new token and code for this user
        token = UserPendingEmailVerifications.generate_token(user_id)
        code = UserPendingEmailVerifications.generate_code()

        verification.update(
            {
                'token': token,
                'code': code
            }
        )

        db.session.commit()

        recipient = User.query.filter_by(user_id=user_id).one_or_none()

        send_email_verify_email(recipient, token, code)
        
@ns.route('/legal-docs/<int:user_id>/')
class UserLegalDocsApi(Resource):
    """
    Endpoints related to legal documents that users have viewed and signed.
    """

    @token_auth.login_required
    @responds(schema=UserLegalDocsSchema(many=True), api=ns, status_code=200)
    def get(self, user_id):

        check_user_existence(user_id)

        docs = UserLegalDocs.query.filter_by(user_id=user_id).all()

        for doc in docs:
            doc_info = LookupLegalDocs.query.filter_by(idx=doc.doc_id).one_or_none()
            doc.doc_name = doc_info.name
            doc.doc_version = doc_info.version

        return docs

    @token_auth.login_required
    @accepts(schema=UserLegalDocsSchema, api=ns)
    @responds(schema=UserLegalDocsSchema, api=ns, status_code=200)
    def post(self, user_id):

        check_user_existence(user_id)

        if UserLegalDocs.query.filter_by(user_id=user_id, doc_id=request.parsed_obj.doc_id).one_or_none():
            raise IllegalSetting(message=f"A record already exists for the user with user_id {user_id}" \
                                    f" and the doc_id {request.parsed_obj.doc_id}. Please use PUT instead.")

        if not LookupLegalDocs.query.filter_by(idx=request.parsed_obj.doc_id).one_or_none():
            raise GenericNotFound(f"There is no document with doc_id {request.parsed_obj.doc_id}")

        request.parsed_obj.user_id = user_id

        db.session.add(request.parsed_obj)
        db.session.commit()

        doc_info = LookupLegalDocs.query.filter_by(idx=request.parsed_obj.doc_id).one_or_none()
        request.parsed_obj.doc_name = doc_info.name
        request.parsed_obj.doc_version = doc_info.version

        return request.parsed_obj

    @token_auth.login_required
    @accepts(schema=UserLegalDocsSchema, api=ns)
    @responds(schema=UserLegalDocsSchema, api=ns, status_code=200)
    def put(self, user_id):

        check_user_existence(user_id)

        doc = UserLegalDocs.query.filter_by(user_id=user_id, doc_id=request.parsed_obj.doc_id).one_or_none()

        if not doc:
            raise GenericNotFound(f"No record exists for the user with user_id {user_id}" \
                                    f" and doc_id {request.parsed_obj.doc_id}. Please use POST.")

        if not LookupLegalDocs.query.filter_by(idx=request.parsed_obj.doc_id).one_or_none():
            raise GenericNotFound(f"There is no document with doc_id {request.parsed_obj.doc_id}.")

        new_data = request.parsed_obj.__dict__
        del new_data['_sa_instance_state']

        doc.update(new_data)
        db.session.commit()

        doc_info = LookupLegalDocs.query.filter_by(idx=doc.doc_id).one_or_none()
        doc.doc_name = doc_info.name
        doc.doc_version = doc_info.version

        return doc