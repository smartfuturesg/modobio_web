import logging

from sqlalchemy import text

logger = logging.getLogger(__name__)

from datetime import datetime, timedelta
import jwt
import requests
import json

from flask import current_app, g, request, redirect, url_for
from flask_accepts import accepts, responds
from flask_restx import Namespace
from pytz import utc
from sqlalchemy.sql.expression import select
from werkzeug.security import check_password_hash
from werkzeug.exceptions import BadRequest, Unauthorized

from odyssey import db
from odyssey.api.client.models import ClientFertility
from odyssey.api.client.schemas import (
    ClientInfoSchema,
    ClientGeneralMobileSettingsSchema,
    ClientRaceAndEthnicitySchema)
from odyssey.api.lookup.models import LookupSubscriptions, LookupLegalDocs
from odyssey.api.staff.models import StaffRoles
from odyssey.api.staff.schemas import StaffProfileSchema, StaffRolesSchema
from odyssey.api.user.models import (
    User,
    UserActiveCampaignTags,
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
from odyssey.integrations.apple import AppStore
from odyssey.utils import search
from odyssey.utils.auth import token_auth, basic_auth
from odyssey.utils.base.resources import BaseResource
from odyssey.utils.constants import PASSWORD_RESET_URL, DB_SERVER_TIME, PROVIDER_ROLES, STAFF_ROLES
from odyssey.utils import search
from odyssey import db
from odyssey.utils.message import email_domain_blacklisted, send_email
from odyssey.utils.misc import (
    EmailVerification,
    check_user_existence,
    check_client_existence,
    check_staff_existence,
    update_client_subscription,
    verify_jwt)
from odyssey.integrations.active_campaign import ActiveCampaign

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
            email_verification_data = EmailVerification().begin_email_verification(user, True, email = email)
            del user_info['email']
            # respond with verification code in dev/testing
            if any((current_app.config['DEV'], current_app.config['TESTING'])) :
                payload['email_verification_code'] = email_verification_data.get('code')

        
        user.update(user_info)
        db.session.commit()


        return payload

@ns.route('/staff/')
class NewStaffUser(BaseResource):
    @token_auth.login_required(user_type=('staff',), staff_role=('staff_admin', 'system_admin', 'client_services'))
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

        # validate requested roles. Assign user as staff, provider or both
        is_provider = True if any(role in PROVIDER_ROLES for role in staff_info.get('access_roles', [])) else False
        is_staff = True if any(role in STAFF_ROLES for role in staff_info.get('access_roles', [])) else False
        
        user = User.query.filter(User.email.ilike(email)).first()
        if user:
            if user.is_staff or user.is_provider:
                # user account already exists for this email and is already a staff/provider account
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
                user_info['is_staff'] = is_staff
                user_info['is_provider'] = is_provider
                user_info['was_staff'] = True
                user.update(user_info)
                
                user_login = db.session.execute(select(UserLogin).filter(UserLogin.user_id == user.user_id)).scalars().one_or_none()
                if user_login:
                    user_login.set_password(password)
                else:
                    user_login = UserLoginSchema().load({"user_id": user.user_id, "password": password})
                    db.session.add(user_login)
                db.session.flush()
                verify_email = True
            else:
                # user account exists but only the client portion of the account is defined
                user.is_staff = True
                user.was_staff = True
                del user_info['password']
                user.update(user_info)

                if user.email_verified:
                    verify_email = False

                    if not any((current_app.config['DEV'], current_app.config['TESTING'])):
                        #User already exists and email is verified.
                        #Check if contact exists in Active Campaign, if not create contact. 
                        ac = ActiveCampaign()
                        if not ac.check_contact_existence(user.user_id):
                            ac.create_contact(user.email, user.firstname, user.lastname)
                            ac.add_age_group_tag(user.user_id)
                        ac.add_tag(user.user_id, 'Persona - Provider')
                else:
                    verify_email = True
        else:
            # user account does not yet exist for this email
            # require password
            password = user_info.get('password', None)
            if not password:
                raise BadRequest('Password required.')

            del user_info['password']
            
            user_info["is_client"] = False
            user_info['is_staff'] = is_staff
            user_info['is_provider'] = is_provider
            user_info["was_staff"] = True
            # create entry into User table first
            # use the generated user_id for UserLogin & StaffProfile tables
            user = UserSchema().load(user_info)
            db.session.add(user) 
            db.session.flush()

            user_login = UserLoginSchema().load({"user_id": user.user_id, "password": password})
            db.session.add(user_login)

            verify_email = True

        if verify_email:
            email_verification_data = EmailVerification().begin_email_verification(user, False)
        
        # create subscription entry for new staff user
        staff_sub = UserSubscriptionsSchema().load({
                'subscription_status': 'subscribed',
                'is_staff': True
            })
        staff_sub.user_id = user.user_id
        db.session.add(staff_sub)

        # add staff_profile for user
        staff_profile = StaffProfileSchema().load({"user_id": user.user_id})
        db.session.add(staff_profile)

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
        subscription_update = False
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
                user_info['was_staff'] = False
                user.update(user_info)
                
                user_login = db.session.execute(select(UserLogin).filter(UserLogin.user_id == user.user_id)).scalars().one_or_none()
                if user_login:
                    user_login.set_password(password)
                else:
                    user_login = UserLoginSchema().load({"user_id": user.user_id, "password": password})
                    db.session.add(user_login)
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
                if user.email_verified:
                    # email already verified, no need to send verification email
                    # update client subscription status if necessary
                    verify_email = False
                    subscription_update = True

                    if not any((current_app.config['DEV'], current_app.config['TESTING'])):
                        #User already exists and email is verified.
                        #Check if contact exists in Active Campaign, if not create contact. 
                        ac = ActiveCampaign()
                        if not ac.check_contact_existence(user.user_id):
                            ac.create_contact(user.email, user.firstname, user.lastname)
                            ac.add_age_group_tag(user.user_id)
                            ac.add_user_subscription_type(user.user_id)
                        ac.add_tag(user.user_id, 'Persona - Client')
                else:
                    verify_email = True
        else:
            # user account does not yet exist for this email
            password=user_info.get('password', None)
            if not password:
                raise BadRequest('Password required.')

            del user_info['password']
            user_info['is_client'] = True
            user_info['is_staff'] = False
            user_info['was_staff'] = False
            user = UserSchema().load(user_info)
            db.session.add(user)
            db.session.flush()
            user_login = UserLoginSchema().load({"user_id": user.user_id, "password": password})
            db.session.add(user_login)

            verify_email = True

        if verify_email:
            email_verification_data = EmailVerification().begin_email_verification(user, False)

            # #Authenticate newly created client account for immediate login
            user, user_login, _ = basic_auth.verify_password(username=user.email, password=password)

        client_info = ClientInfoSchema().load({"user_id": user.user_id})
        db.session.add(client_info)
        
        # add new client subscription information
        client_sub = UserSubscriptionsSchema().load({
            'subscription_status': 'unsubscribed',
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

        # Generate access and refresh tokens
        access_token = UserLogin.generate_token(user_type='client', user_id=user.user_id, token_type='access')
        refresh_token = UserLogin.generate_token(user_type='client', user_id=user.user_id, token_type='refresh')
        
        # Add refresh token to db
        db.session.add(UserTokenHistory(user_id=user.user_id, 
                                        refresh_token=refresh_token,
                                        event='login',
                                        ua_string = request.headers.get('User-Agent')))

        db.session.commit()

        if subscription_update:
            # checks for any existing subscriptions and updates the client subscription status
            update_client_subscription(user_id=user.user_id)

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
        token = {
            'exp': datetime.utcnow() + timedelta(minutes=15),
            'sid': user.user_id}
        password_reset_token = jwt.encode(token, secret, algorithm='HS256')

        send_email(
            'password-reset',
            user.email,
            name=user.firstname,
            email=user.email,
            reset_password_url=PASSWORD_RESET_URL.format(url_scheme, password_reset_token))

        # DEV mode won't send an email, so return password. DEV mode ONLY.
        if current_app.config['DEV']:
            res['token'] = password_reset_token
            res['password_reset_url'] = PASSWORD_RESET_URL.format(url_scheme, password_reset_token)

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

        # Make sure user does not enter the previous password as the new password
        if check_password_hash(user.password, pswd):
            raise BadRequest('New password must be different than the old password.')

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

        # Check that the user entered the correct current password
        if check_password_hash(user_login.password, request.parsed_obj['current_password']):
            # Make sure user does not enter the previous password as the new password
            if check_password_hash(user_login.password, request.parsed_obj['new_password']):
                raise BadRequest('New password must be different than the old password.')

            user_login.set_password(request.parsed_obj['new_password'])
        else:
            raise Unauthorized

        db.session.commit()

        return 200

@ns.route('/token/refresh')
@ns.doc(params={'refresh_token': "token from password reset endpoint"})
class RefreshToken(BaseResource):
    """User refresh token to issue a new token with a 1 hr TTL"""
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
        #pass new lifetime here
        new_refresh_token = UserLogin.generate_token(user_id=decoded_token['uid'], user_type=decoded_token['utype'], token_type='refresh', refresh_token_lifetime=decoded_token['ttl'])  
        
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

@ns.route('/subscription/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class UserSubscriptionApi(BaseResource):
    __check_resource__ = False

    @token_auth.login_required(user_type=('staff', 'client'), staff_role=('client_services',))
    @responds(schema=UserSubscriptionsSchema, api=ns, status_code=200)
    def get(self, user_id):
        """
        Returns active subscription information for the given user_id. 
        Because a user_id can belong to both a client and staff account, both active subscriptions will be returned in this case.
        """
        check_user_existence(user_id)
        
        # bring up most recent subscription
        current_subscription = UserSubscriptions.query.filter_by(user_id=user_id, is_staff=True if g.user_type == 'staff' else False).order_by(UserSubscriptions.idx.desc()).first()

        renewal_info = None
        if current_subscription.apple_original_transaction_id and current_subscription.subscription_status == 'subscribed':
            appstore  = AppStore()
            _, renewal_info, _ = appstore.latest_transaction(current_subscription.apple_original_transaction_id)

        if renewal_info:
            current_subscription.auto_renew_status = True if renewal_info.get('autoRenewStatus') == 1 else False

        if current_subscription.sponsorship:
            sponsoring_user = User.query.filter_by(user_id=current_subscription.sponsorship.user_id).one_or_none()
            current_subscription.__dict__["sponsorship"] = {
                "sponsor": current_subscription.sponsorship.sponsor, 
                "first_name": sponsoring_user.firstname, 
                "last_name": sponsoring_user.lastname, 
                "modobio_id": sponsoring_user.modobio_id
            }
        return current_subscription

    @token_auth.login_required(user_type=('staff-self', 'client'))
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

        user, _ = token_auth.current_user()

        if request.parsed_obj.apple_original_transaction_id:
           update_client_subscription(user_id = user_id, apple_original_transaction_id =  request.parsed_obj.apple_original_transaction_id)
        
        elif not request.parsed_obj.is_staff and not request.parsed_obj.apple_original_transaction_id:
            raise BadRequest('Missing original transaction id')

        # Update the previous subscription if necessary
        if prev_sub.subscription_status == 'subscribed':
            if prev_sub.expire_date:
                if prev_sub.expire_date < datetime.utcnow() or transaction_info.get('productId') != prev_sub.subscription_type_information.ios_product_id:
                    prev_sub.update({'end_date': datetime.fromtimestamp(transaction_info['purchaseDate']/1000, utc).replace(tzinfo=None), 'subscription_status': 'unsubscribed', 'last_checked_date': datetime.utcnow().isoformat()})
                else:
                    # new subscription entry not required return the current subscription
                    prev_sub.auto_renew_status = True if renewal_info.get('autoRenewStatus') == 1 else False
                    prev_sub.update({'last_checked_date': datetime.utcnow().isoformat()})
                    db.session.commit()
                    return prev_sub
        else:
            prev_sub.update({'end_date': datetime.fromtimestamp(transaction_info['purchaseDate']/1000, utc).replace(tzinfo=None),'last_checked_date': datetime.utcnow().isoformat()})
    
            # if this subscription is following an unsubscribed status: 
            #   either first time subscription or first subscription ever
            # Send a Welcome email
            send_email('subscription-confirm', user.email, firstname=user.firstname)
                
        # make a new subscription entry
        new_data = {
            'subscription_status': request.parsed_obj.subscription_status,
            'subscription_type_id': request.parsed_obj.subscription_type_id,
            'is_staff': request.parsed_obj.is_staff,
            'apple_original_transaction_id': request.parsed_obj.apple_original_transaction_id,
            'last_checked_date': datetime.utcnow().isoformat()
        }

        new_sub = UserSubscriptionsSchema().load(new_data)
        new_sub.user_id = user_id

        if request.parsed_obj.apple_original_transaction_id:
            new_sub.auto_renew_status = True if renewal_info.get('autoRenewStatus') == 1 else False
            new_sub.expire_date = datetime.fromtimestamp(transaction_info['expiresDate']/1000, utc).replace(tzinfo=None)
            new_sub.start_date = datetime.fromtimestamp(transaction_info['purchaseDate']/1000, utc).replace(tzinfo=None)
        
        db.session.add(new_sub)
        db.session.commit()

        current_subscription = UserSubscriptions.query.filter_by(user_id=user_id, is_staff=True if g.user_type == 'staff' else False).order_by(UserSubscriptions.idx.desc()).first()

        return current_subscription


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
        for i, client_subscription in enumerate(client_history):
            if client_subscription.sponsorship:
                sponsoring_user = User.query.filter_by(user_id=client_subscription.sponsorship.user_id).one_or_none()
                client_subscription.__dict__["sponsorship"] = {
                    "sponsor": client_subscription.sponsorship.sponsor, 
                    "first_name": sponsoring_user.firstname, 
                    "last_name": sponsoring_user.lastname, 
                    "modobio_id": sponsoring_user.modobio_id
                }
                client_history[i] = client_subscription
                
        staff_history = UserSubscriptions.query.filter_by(user_id=user_id).filter_by(is_staff=True).all()

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
        """ Verify the user's email address.

        Verifying an email requires both a valid code that the client retrieved
        from their email and a valid token stored on the modobio side. The token
        has a short lifetime so the email verification process must happen within
        that time. 

        Parameters
        ----------
        user_id : int
            User ID number

        code : str
            email verification code provided during client creation
        """
        EmailVerification().complete_email_verification(user_id = user_id, code = request.args.get('code'))
        
        user = User.query.filter_by(user_id=user_id).one_or_none()
        
        #Only run active campaign operations in prod
        if not any((current_app.config['DEV'], current_app.config['TESTING'])):
            #Add to Active Campaign after email_verification
            ac = ActiveCampaign()    
            if not ac.check_contact_existence(user_id):
                ac.create_contact(user.email, user.firstname, user.lastname)
            #Add user type tag
            if user.is_client:
                ac.add_tag(user_id, 'Persona - Client')
            if user.is_staff:
                ac.add_tag(user_id, 'Persona - Provider')
            #Add subcription tag
            ac.add_user_subscription_type(user_id)
            #Add age group tag
            ac.add_age_group_tag(user_id)
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
        verification.token = UserPendingEmailVerifications.generate_token(user_id)
        verification.code = UserPendingEmailVerifications.generate_code()

        db.session.commit()

        user = User.query.filter_by(user_id=user_id).one_or_none()

        link = url_for(
            '.user_user_pending_email_verifications_token_api',
            token=verification.token,
            _external=True)

        send_email(
            'email-verify',
            user.email,
            name=user.firstname,
            verification_link=link,
            verification_code=verification.code)

        
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