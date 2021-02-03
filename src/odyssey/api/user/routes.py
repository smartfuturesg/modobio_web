from datetime import datetime, timedelta
import boto3
import jwt

from flask import current_app, request, jsonify
from flask_accepts import accepts, responds
from flask_restx import Resource
from werkzeug.security import check_password_hash


from odyssey.api import api
from odyssey.api.client.schemas import ClientInfoSchema
from odyssey.api.lookup.models import LookupSubscriptions
from odyssey.api.staff.schemas import StaffProfileSchema, StaffRolesSchema
from odyssey.api.user.models import User, UserLogin, UserRemovalRequests, UserSubscriptions, UserTokensBlacklist
from odyssey.api.staff.models import StaffRoles
from odyssey.api.user.schemas import (
    UserSchema, 
    UserLoginSchema,
    UserPasswordRecoveryContactSchema,
    UserPasswordResetSchema,
    UserPasswordUpdateSchema,
    UserInfoSchema,
    UserSubscriptionsSchema,
    UserSubscriptionHistorySchema,
    NewStaffUserSchema,
) 
from odyssey.utils.auth import token_auth
from odyssey.utils.constants import PASSWORD_RESET_URL, DB_SERVER_TIME
from odyssey.utils.errors import InputError, StaffEmailInUse, ClientEmailInUse, UnauthorizedUser
from odyssey.utils.email import send_email_password_reset, send_email_delete_account
from odyssey.utils.misc import check_user_existence, check_client_existence, check_staff_existence, verify_jwt

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

    @token_auth.login_required()
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
        breakpoint()
        #Get a list of all tables in database
        tableList = db.session.execute("SELECT distinct(table_name) from information_schema.columns\
                WHERE column_name='user_id';").fetchall()
        
        #Send notification email to user being deleted and user requesting deletion
        #when FLASK_ENV=production
        if user.email != requester.email:
            send_email_delete_account(requester.email, user.email)
        send_email_delete_account(user.email, user.email)

        if user.is_staff:
            #keep name, email, modobio id, user id in User table
            #keep lines in tables where user_id is the reporter_id
            user.phone_number = None
        else:#it's client
            #keep only modobio id, user id in User table
            user.email = None
            user.phone_number = None
            user.firstname = None
            user.middlename = None
            user.lastname = None
            
        #delete files or images saved in S3 bucket for user_id
        #when FLASK_DEV=remote
        if not current_app.config['LOCAL_CONFIG']:
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
            
        # create entries for role assignments 
        for role in staff_info.get('access_roles', []):
            db.session.add(StaffRolesSchema().load(
                                            {'user_id': user.user_id,
                                             'role': role}
                                            ))
            

        db.session.commit()
        db.session.refresh(user)
        payload = user.__dict__
        payload["staff_info"] = {"access_roles": staff_info.get('access_roles', []) }
        payload["user_info"] =  user
        return payload


@ns.route('/staff/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class StaffUserInfo(Resource):
    @token_auth.login_required
    @responds(schema=NewStaffUserSchema, status_code=200, api=ns)
    def get(self, user_id):
        user = User.query.filter_by(user_id=user_id).one_or_none()
        staff_roles = db.session.query(StaffRoles.role).filter(StaffRoles.user_id==user_id).all()

        access_roles = []
        for role in staff_roles:
            access_roles.append(role.role)

        payload = {
                    "staff_info": 
                        {
                            "access_roles": access_roles
                        },
                    "user_info": 
                        user}
        return payload

@ns.route('/client/')
class NewClientUser(Resource):
    @accepts(schema=UserInfoSchema, api=ns)
    @responds(schema=UserInfoSchema, status_code=201, api=ns)
    def post(self): 
        """
        Create a client user. This endpoint requires a payload with just userinfo.
        
        If registering an already existing staff user as a client, 
        the password must match, or be and empty string (ie. "")
        """
        user_info = request.get_json()   
          
        user = User.query.filter(User.email.ilike(user_info.get('email'))).first()
        if user:
            if user.is_client:
                # user account already exists for this email and is already a client account
                raise ClientEmailInUse(email=user_info.get('email'))
            else:
                # user account exists but only the staff portion of the account is defined
                user.is_client = True
                client_info = ClientInfoSchema().load({'user_id': user.user_id})
                password=""
                db.session.add(client_info)

                # add new client subscription information
                client_sub = UserSubscriptionsSchema().load({
                    'subscription_status': 'unsubscribed',
                    'subscription_type_id': 1,
                    'is_staff': False
                })
                client_sub.user_id = user.user_id
                db.session.add(client_sub)
        else:
            # user account does not yet exist for this email
            password=user_info.get('password')
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

            # add new user subscription information
            client_sub = UserSubscriptionsSchema().load({
                'subscription_status': 'unsubscribed',
                'subscription_type_id': 1,
                'is_staff': False
            })
            client_sub.user_id = user.user_id
            db.session.add(client_sub)

        payload=user.__dict__
        payload['password']=password
        
        db.session.commit()

        payload['user_info'] = user
        
        return user

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
                                  algorithm='HS256').decode("utf-8") 
                                  
        send_email_password_reset(user.email, password_reset_token)

        if current_app.env == "development":
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
            raise InputError(message="invalid token", status_code=401)

        # check that the token is valid
        decoded_token = verify_jwt(refresh_token)
        
        # if valid, create a new access token, return it in the payload
        access_token = UserLogin.generate_token(user_id=decoded_token['uid'], user_type=decoded_token['utype'], token_type='access')
        new_refresh_token = UserLogin.generate_token(user_id=decoded_token['uid'], user_type=decoded_token['utype'], token_type='refresh')  
        
        # update user login details with latest refresh token
        user_login_details = UserLogin.query.filter_by(user_id = decoded_token['uid']).one_or_none()
        user_login_details.refresh_token = new_refresh_token

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

