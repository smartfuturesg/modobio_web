import logging
logger = logging.getLogger(__name__)

from datetime import datetime, timedelta
import secrets
import jwt

from flask import current_app, request
from flask_accepts import accepts, responds
from flask_restx import Namespace
from werkzeug.exceptions import BadRequest

from odyssey import db
from odyssey.api import api
from odyssey.api.client_services.schemas import NewRemoteRegisterUserSchema, NewUserRegistrationPortalSchema
from odyssey.api.user.schemas import UserLoginSchema, UserSchema, UserSubscriptionsSchema
from odyssey.api.user.models import User, UserLogin
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource
from odyssey.utils.constants import REGISTRATION_PORTAL_URL
from odyssey.utils.message import send_email_user_registration_portal

ns = Namespace('client-services', description='Endpoints for client services operations.')

@ns.route('/user/new/')
class NewUserClientServices(BaseResource):
    """
    Create, Update, Retrieve user basic information. 
    This endpoint is intended to be used by client services. 
    """

    @token_auth.login_required(user_type=('staff', ), staff_role=('client_services',))
    @accepts(schema=NewRemoteRegisterUserSchema, api=ns)
    @responds(schema=NewUserRegistrationPortalSchema, api=ns, status_code=201)
    def post(self):
        """
        Create new user using only email (and/or phone number) and name. Returns a password and portal link for the new user.
        Portal link includes a portal_id which is a JWT with a 72 hour lifetime. New Users must use this link to complete their registration.
        
        This API will create a new account but not will assign the account to a user context ('client' or 'staff'). To complete registration,
        users must have their portal_id verified by another API. At this step, the user's context will be assigned in the database so 
        they may go ahead and request an API token (log in).
        
        """
        data = request.parsed_obj
        user_type = data.get('user_type')
        del data['user_type']
        email = data.get('email', '')
        user = User.query.filter(User.email.ilike(email.lower())).first()
        if user:
            raise BadRequest(f'Email {email} already in use.')
        password = email[:2] + secrets.token_hex(8)
        data['is_client'] = False
        data['is_staff'] = False
        user = UserSchema().load(data)
        db.session.add(user)
        db.session.flush()

        user_id = user.user_id

        user_login = UserLoginSchema().load({'user_id': user_id,  'password':password})
        db.session.add(user_login)

        # add new user subscription information
        client_sub = UserSubscriptionsSchema().load({
            'subscription_type_id': 1,
            'subscription_status': 'unsubscribed',
            'is_staff': False
        })
        client_sub.user_id = user.user_id
        db.session.add(client_sub)
        db.session.commit()

        secret = current_app.config['SECRET_KEY']
        portal_id = jwt.encode({'exp': datetime.utcnow() + timedelta(hours=72),  
                                'utype': user_type,
                                'uid': user_id},
                                secret,
                                algorithm='HS256')

        send_email_user_registration_portal(user.email, password, portal_id)

        # DEV mode won't send an email, so return password. DEV mode ONLY.
        if current_app.config['DEV']:
            return {'password':password,
                    'portal_id': portal_id,
                    'registration_portal_url': REGISTRATION_PORTAL_URL.format(portal_id)}


@ns.route("/user/registration-portal/refresh")
class RefreshRegistrationPortal(BaseResource):
    """
    Routines related to registration portals.

    """
    @token_auth.login_required(user_type=('staff', ), staff_role=('client_services',))
    @accepts(dict(name='email', type=str), dict(name='user_type', type=str), api=ns)
    @responds(schema=NewUserRegistrationPortalSchema, api=ns, status_code=201)
    def put(self):
        """
        Takes the email of a client already in the system and
        returns a fresh portal_id and registration url so the client can continue their registration.

        This API can be used as part of the creation of a new user account or to assign a user new 
        privileges (like registering a current client account as a staff account)

        With a portal_id, clients will be able to complete their registration of either a brand new account
        or an account that's been updated to include a new staff or client side. 

        user_type must be either 'client' or 'staff'
        """
        email = request.parsed_args.get('email')
        user_type = request.parsed_args.get('user_type')
        if user_type not in ('staff', 'client'):
            raise BadRequest('Wrong user type.')

        user = User.query.filter_by(email=email.lower()).one_or_none()
        if not user:
            raise BadRequest('User not found.')

        # reset the user's password, send that password as part of the registration portal email
        user_login = UserLogin.query.filter_by(user_id=user.user_id).one_or_none()
        password = user.email[:2] + secrets.token_hex(8)

        user_login.set_password(password)

        secret = current_app.config['SECRET_KEY']
        portal_id = jwt.encode({'exp': datetime.utcnow() + timedelta(hours=72),  
                                'utype': user_type,
                                'uid': user.user_id},
                                secret,
                                algorithm='HS256')

        send_email_user_registration_portal(user.email, password, portal_id)
        
        db.session.commit()

        # DEV mode won't send an email, so return password. DEV mode ONLY.
        if current_app.config['DEV']:
            return {'password':password,
                    'portal_id': portal_id,
                    'registration_portal_url': REGISTRATION_PORTAL_URL.format(portal_id)}
