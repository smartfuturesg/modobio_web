import logging
logger = logging.getLogger(__name__)

from datetime import datetime, timedelta
import jwt
import requests
import json

from flask import current_app, request, redirect
from flask_accepts import accepts, responds
from flask_restx import Resource, Namespace
from sqlalchemy.sql.expression import select
from werkzeug.security import check_password_hash
from werkzeug.exceptions import BadRequest, Unauthorized

from odyssey import db
from odyssey.api import api
from odyssey.api.client.models import ClientClinicalCareTeam, ClientFertility
from odyssey.api.client.schemas import (
    ClientInfoSchema,
    ClientGeneralMobileSettingsSchema,
    ClientRaceAndEthnicitySchema)
from odyssey.api.lookup.models import LookupSubscriptions, LookupLegalDocs
from odyssey.api.staff.models import StaffRoles
from odyssey.api.staff.schemas import StaffProfileSchema, StaffRolesSchema
from odyssey.api.user.models import (
    User,
    UserLogin,
    UserRemovalRequests,
    UserSubscriptions,
    UserTokenHistory,
    UserTokensBlacklist,
    UserPendingEmailVerifications,
    UserLegalDocs, 
    UserResetPasswordRequestHistory
)
from odyssey.api.user.schemas import (
    UserInfoPutSchema,
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
from odyssey.utils import search
from odyssey.utils.auth import token_auth, basic_auth
from odyssey.utils.base.resources import BaseResource
from odyssey.utils.constants import PASSWORD_RESET_URL, DB_SERVER_TIME
from odyssey.utils.file_handling import FileHandling
from odyssey.utils import search
from odyssey import db
from odyssey.utils.message import (
    email_domain_blacklisted,
    send_email_password_reset,
    send_email_delete_account,
    send_email_verify_email)
from odyssey.utils.misc import (
    EmailVerification,
    check_user_existence,
    check_client_existence,
    check_staff_existence,
    generate_modobio_id,
    verify_jwt)

ns = Namespace('user', description='Endpoints for user accounts.')


@ns.route('/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ApiUser(BaseResource):
    """
    Retrieve, Update, and Delete a User's basic information.
    """
    
    @token_auth.login_required
    @responds(schema=UserSchema, api=ns)
    def get(self, user_id):
        check_user_existence(user_id)

        return User.query.filter_by(user_id=user_id).one_or_none()

    @token_auth.login_required(user_type=('staff', 'client', 'staff_self'), staff_role=('client_services',))
    @accepts(schema=UserInfoPutSchema)
    @responds(schema=NewClientUserSchema, status_code=200)
    def patch(self, user_id):
        """
        Update attributes from user's basic info. See api.user.schemas.UserInfoPutSchema for attributes that can be updated. 
        
        Client services role will have access to this endpoint. All other staff roles are locked out unless editing their own resource. 
        """
        user = self.check_user(user_id)

        user_info = request.json
        email = user_info.get('email')

        payload = {}
        #if email is part of payload, use email update routine
        if email:
            email_domain_blacklisted(email)
            email_verification_data = EmailVerification().begin_email_verification(user, email = email)
            del user_info['email']
        
        user.update(user_info)
        db.session.commit()

        # respond with verification code in dev
        if any((current_app.config['DEV'], current_app.config['TESTING'])) :
            payload['email_verification_code'] = email_verification_data.get('code')

        return payload


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
        fh = FileHandling()
        fh.delete_from_s3(prefix=f'id{user_id:05d}/')
        
        #Get a list of all tables in database that have fields: client_user_id & staff_user_id
        # NOTE - Order matters, must delete these tables before those with user_id 
        # to avoid problems while deleting payment methods
        tableList = db.session.execute("SELECT distinct(table_name) from information_schema.columns\
                WHERE column_name='staff_user_id' OR column_name='client_user_id';").fetchall()
        
        #delete lines with user_id in all other tables except "User" and "UserRemovalRequests"
        for table in tableList:
            tblname = table.table_name
            #Only delete telehealth bookings when the client is being deleted, keep if it's the practitioner
            if tblname == 'TelehealthBookings':
                db.session.execute(f"DELETE FROM \"{tblname}\" WHERE client_user_id={user_id};")
            else:
                db.session.execute(f"DELETE FROM \"{tblname}\" WHERE staff_user_id={user_id} OR client_user_id={user_id};")

        #Get a list of all tables in database that have field: user_id
        tableList = db.session.execute("SELECT distinct(table_name) from information_schema.columns\
                WHERE column_name='user_id';").fetchall()

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
class NewStaffUser(BaseResource):
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
        # Check if user exists already
        user_info = request.json['user_info']
        email = user_info['email']

        email_domain_blacklisted(email)

        # Email address is lower-cased to make comparison easier.
        # However:
        # - The local part of the email address (before @) is case-sensitive according to specs,
        #   even though hosts are recommended to handle addresses in a case-independent manner.
        #   So Zan.Peeters should be delivered to zan.peeters mailbox, but not every host
        #   implements this behaviour, in which case they are two separate mailboxes.
        # - Internationalization allows for addresses and domains to be written in any script.
        #   Upper/lower case is not trivial in every language (e.g. Turkish dotless-i, Greek sigma).
        # More info:
        # https://en.wikipedia.org/wiki/Email_address
        # https://unicode.org/reports/tr46/
        # Leaving this behaviour for now, until it becomes a problem.
        email = user_info['email'] = email.lower()

        staff_info = request.json.get('staff_info')

        user = User.query.filter(User.email.ilike(email)).first()
        if user:
            if user.is_staff:
                # user account already exists for this email and is already a staff account
                raise BadRequest('Email address {email} already exists.')

            elif user.is_client == False and user.is_staff == False:
                # user is neither a staff or client user
                # currently, this can be the case when the user has been added by another user through the clinical
                # care team system. the user info provided will populate the already existing user entry and the 
                # password given will overwrite the password in the UserLogin entry (if it exist)

                password=user_info.get('password', None)
                
                if not password:
                    raise BadRequest('Password required.')
                
                del user_info['password']
                user_info['is_client'] = False
                user_info['is_staff'] = True
                user.update(user_info)
                
                user_login = db.session.execute(select(UserLogin).filter(UserLogin.user_id == user.user_id)).scalars().one_or_none()
                if user_login:
                    user_login.set_password(password)
                else:
                    user_login = UserLoginSchema().load({"user_id": user.user_id, "password": password})
                    db.session.add(user_login)
                
                client_info = ClientInfoSchema().load({"user_id": user.user_id})
                db.session.add(client_info)
                db.session.flush()
                verify_email = True
            else:
                #user account exists but only the client portion of the account is defined
                user.is_staff = True
                staff_profile = StaffProfileSchema().load({'user_id': user.user_id})
                db.session.add(staff_profile)
                user.update(user_info)

                # add new staff subscription information
                staff_sub = UserSubscriptionsSchema().load({
                    'subscription_type_id': 1,
                    'subscription_status': 'subscribed',
                    'is_staff': True
                })
                staff_sub.user_id = user.user_id
                db.session.add(staff_sub)

                verify_email = False
        else:
            # user account does not yet exist for this email
            # require password
            password = user_info.get('password', None)
            if not password:
                raise BadRequest('Password required.')

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
                'subscription_type_id': 1,
                'subscription_status': 'subscribed',
                'is_staff': True
            })
            staff_sub.user_id = user.user_id
            db.session.add(staff_sub)

            verify_email = True

        if verify_email:
            email_verification_data = EmailVerification().begin_email_verification(user)
        
        # create entries for role assignments 
        for role in staff_info.get('access_roles', []):
            db.session.add(StaffRolesSchema().load(
                                            {'user_id': user.user_id,
                                             'role': role,
                                             'granter_id': token_auth.current_user()[0].user_id}
                                            ))

        db.session.commit()
        db.session.refresh(user)
        payload = user.__dict__
        payload["staff_info"] = {"access_roles": staff_info.get('access_roles', []), 
                                "access_roles_v2": StaffRoles.query.filter_by(user_id = user.user_id)}
    
        payload["user_info"] =  user

        # respond with verification code in dev
        if current_app.config['DEV'] and verify_email:
            payload['email_verification_code'] = email_verification_data.get('code')

        return payload


@ns.route('/staff/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class StaffUserInfo(BaseResource):
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
class NewClientUser(BaseResource):
    @accepts(schema=UserInfoSchema, api=ns)
    @responds(schema=NewClientUserSchema, status_code=201, api=ns)
    def post(self): 
        """
        Create a client user. This endpoint requires a payload with just userinfo.

        If registering an already existing staff user as a client, 
        the password provided must match the one already in use by staff account
        """
        user_info = request.json
        email = user_info['email']

        email_domain_blacklisted(email)

        # Email address is lower-cased to make comparison easier.
        # However:
        # - The local part of the email address (before @) is case-sensitive according to specs,
        #   even though hosts are recommended to handle addresses in a case-independent manner.
        #   So Zan.Peeters should be delivered to zan.peeters mailbox, but not every host
        #   implements this behaviour, in which case they are two separate mailboxes.
        # - Internationalization allows for addresses and domains to be written in any script.
        #   Upper/lower case is not trivial in every language (e.g. Turkish dotless-i, Greek sigma).
        # More info:
        # https://en.wikipedia.org/wiki/Email_address
        # https://unicode.org/reports/tr46/
        # Leaving this behaviour for now, until it becomes a problem.
        email = user_info['email'] = email.lower()

        user = db.session.execute(select(User).filter(User.email == email)).scalars().one_or_none()
        if user:
            if user.is_client:
                # user account already exists for this email and is already a client account
                raise BadRequest('Email address {email} already exists.')
            elif user.is_client == False and user.is_staff == False:
                # client is neither a staff or client user
                # currently, this can be the case when the user has been added by another user through the clinical
                # care team system. the user info provided will populate the already existing user entry and the 
                # password given will overwrite the password in the UserLogin entry (if it exist)

                password=user_info.get('password', None)
                
                if not password:
                    raise BadRequest('Password required.')
                
                del user_info['password']
                user_info['is_client'] = True
                user_info['is_staff'] = False
                user.update(user_info)
                
                user_login = db.session.execute(select(UserLogin).filter(UserLogin.user_id == user.user_id)).scalars().one_or_none()
                if user_login:
                    user_login.set_password(password)
                else:
                    user_login = UserLoginSchema().load({"user_id": user.user_id, "password": password})
                    db.session.add(user_login)
                client_info = ClientInfoSchema().load({"user_id": user.user_id})
                db.session.add(client_info)
                db.session.flush()
                verify_email = True

            else:
                # user account exists but only the staff portion of the account is defined
                #verify password matches already existing staff login info before allowing client access
                password= user_info.get('password')
                del user_info['password']
                user, user_login, _ = basic_auth.verify_password(username=user.email, password=password)
                user.update(user_info)
                #Create client account for existing staff member
                user.is_client = True
                client_info = ClientInfoSchema().load({'user_id': user.user_id})
                
                db.session.add(client_info)
                verify_email = False
        else:
            # user account does not yet exist for this email
            password=user_info.get('password', None)
            if not password:
                raise BadRequest('Password required.')

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

            verify_email = True

        if verify_email:
            email_verification_data = EmailVerification().begin_email_verification(user)

            # #Authenticate newly created client account for immediate login
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
        
        # if client biological_sex_male = False, add default fertility status
        if 'biological_sex_male' in user_info:
            if not user_info['biological_sex_male']:
                fertility = ClientFertility(**{'pregnant': False, 'status': 'unknown'})
                fertility.user_id = user.user_id
                db.session.add(fertility)

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

        # respond with verification code in dev
        if current_app.config['DEV'] and verify_email:
            payload['email_verification_code'] = email_verification_data.get('code')

        return payload

@ns.route('/password/forgot-password/recovery-link/')
class PasswordResetEmail(BaseResource):
    """Password reset endpoints."""
    
    @accepts(schema=UserPasswordRecoveryContactSchema, api=ns)
    @responds(schema=UserPasswordRecoveryContactSchema, status_code=200, api=ns)
    def post(self):
        """begin a password reset session. 
            Staff member unable to log in will request a password reset
            with only their email. Emails will be checked for exact match in the database
            to a staff member. If outside of the dev environment, a Google ReCaptcha response
            must be provided. If a recaptcha response is not provided in the dev environment, captcha
            verification will be skipped.
    
            If the email exists, a signed JWT is created; encoding the token's expiration 
            time and the user_id. The code will be placed into this URL <url for password reset>
            and sent to a valid email address.  
            If the email does not exist, no email is sent. 
            response 200 OK
        """
        email = request.parsed_obj['email']
        if not email:
            raise BadRequest('Email address required.')

        res = {}

        # verify Google ReCaptcha - optional if in dev environment, otherwise required. () for clarity
        if (current_app.config['DEV'] and 'captcha_key' in request.parsed_obj) or not current_app.config['DEV']:
            request_data = {
                'secret': current_app.config['GOOGLE_RECAPTCHA_SECRET'],
                'response': request.parsed_obj['captcha_key']
            }

            response = requests.post('https://www.google.com/recaptcha/api/siteverify',
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    data=request_data)

            res = json.loads(response.text)
            if 'error-codes' in res:
                res['error_codes'] = res['error-codes']
                
            # if captcha verification failed, return here rather than starting the password reset process
            if not res['success']:
                return res

        # collect user agent string from request headers
        ua_string = request.headers.get('User-Agent')

        # TODO save request history in logs, not db
        request_history = UserResetPasswordRequestHistory()
        request_history.ua_string = ua_string
        request_history.email = email

        # verify the email provided belongs to a user
        user = User.query.filter_by(email=email.lower()).first()
        if not user:
            db.session.add(request_history)
            db.session.commit()
            return 200
        
        request_history.user_id = user.user_id
        db.session.add(request_history)
        db.session.commit()

        # url_scheme specific to version of app requesting it. 
        # For mobile, this should be a universal link that tries to open the app
        url_scheme = f'https://{current_app.config["FRONT_END_DOMAIN_NAME"]}'

        secret = current_app.config['SECRET_KEY']
        password_reset_token = jwt.encode({'exp': datetime.utcnow()+timedelta(minutes = 15), 
                                  'sid': user.user_id}, 
                                  secret, 
                                  algorithm='HS256')       
                
        send_email_password_reset(user, password_reset_token, url_scheme)

        # DEV mode won't send an email, so return password. DEV mode ONLY.
        if current_app.config['DEV']:
            res['token'] = password_reset_token
            res['password_reset_url'] = PASSWORD_RESET_URL.format(url_scheme,password_reset_token)

        return res
        

@ns.route('/password/forgot-password/reset')
@ns.doc(params={'reset_token': "token from password reset endpoint"})
class ResetPassword(BaseResource):
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
            raise Unauthorized('Token authorization expired.')

        # bring up the staff member and reset their password
        pswd = request.parsed_obj['password']

        user = UserLogin.query.filter_by(user_id=decoded_token['sid']).first()
        user.set_password(pswd)

        db.session.commit()

        return 200

@ns.route('/password/update/')
class ChangePassword(BaseResource):
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
            raise Unauthorized

        db.session.commit()

@ns.route('/token/refresh')
@ns.doc(params={'refresh_token': "token from password reset endpoint"})
class RefreshToken(BaseResource):
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
            raise Unauthorized('Invalid refresh token.')

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
class VerifyPortalId(BaseResource):
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
            raise Unauthorized

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
class UserSubscriptionApi(BaseResource):

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
            raise BadRequest('Invalid subscription type.')

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
class UserSubscriptionHistoryApi(BaseResource):

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
class UserLogoutApi(BaseResource):

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

# TODO: remove these redirects once fixed on frontend

from odyssey.api.notifications.schemas import NotificationSchema

@ns.route('/notifications/<int:user_id>/')
@ns.deprecated
@ns.doc(params={'user_id': 'User ID number'})
class UserNotificationsApi(BaseResource):
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
class UserNotificationsPutApi(BaseResource):
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
class UserPendingEmailVerificationsTokenApi(BaseResource):

    @responds(status_code=200)
    def get(self, token):
        """
        Checks if token has not expired and exists in db.
        If true, removes pending verification object and returns 200.
        """
        EmailVerification().complete_email_verification(token = token)

        return

@ns.route('/email-verification/code/<int:user_id>/')
@ns.doc(params={'code': 'Email verification code'})
class UserPendingEmailVerificationsCodeApi(BaseResource):
    __check_resource__ = False
    
    @responds(status_code=200)
    def post(self, user_id):
        """
        Verify the user's email address.

        Params
        -------
        user_id int
        code: email verification code provided during client creation

        Verifying an email requires both a valid code that the client retrieved from their email and a valid 
        token stored on the modobio side. The token has a short lifetime so the email varification process must happen within
        that time. 
        """
        EmailVerification().complete_email_verification(user_id = user_id, code = request.args.get('code'))

        return

@ns.route('/email-verification/resend/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class UserPendingEmailVerificationsResendApi(BaseResource):
    """
    If a user waited too long to verify their email and their token/code have expired,
    they can use this endpoint to create another token/code and send another email. This 
    can also be used if the user never received an email.
    """
    __check_resource__ = False

    @responds(status_code=200)
    def post(self, user_id):
        verification = UserPendingEmailVerifications.query.filter_by(user_id=user_id).one_or_none()
            
        if not verification:
            raise Unauthorized('Email verification failed.')

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
class UserLegalDocsApi(BaseResource):
    """
    Endpoints related to legal documents that users have viewed and signed.
    """
    
    # Multiple docs per user allowed.
    __check_resource__ = False

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
            raise BadRequest(f'Document {request.parsed_obj.doc_id} already exists.')

        if not LookupLegalDocs.query.filter_by(idx=request.parsed_obj.doc_id).one_or_none():
            raise BadRequest(f'Document {request.parsed_obj.doc_id} not found.')

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
            raise BadRequest(f'Document {request.parsed_obj.doc_id} already exists.')

        if not LookupLegalDocs.query.filter_by(idx=request.parsed_obj.doc_id).one_or_none():
            raise BadRequest(f'Document {request.parsed_obj.doc_id} not found.')

        new_data = request.parsed_obj.__dict__
        del new_data['_sa_instance_state']

        doc.update(new_data)
        db.session.commit()

        doc_info = LookupLegalDocs.query.filter_by(idx=doc.doc_id).one_or_none()
        doc.doc_name = doc_info.name
        doc.doc_version = doc_info.version

        return doc