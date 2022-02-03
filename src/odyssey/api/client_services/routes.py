import logging

from flask import request
from flask_accepts import accepts, responds
from flask_restx import Namespace
from sqlalchemy import select
from werkzeug.exceptions import BadRequest

from odyssey import db
from odyssey.api import api
from odyssey.api.client_services.schemas import (
    CSAccountBlockSchema,
    CSAccountUnblockSchema,
    CSUserSchema,
    CSUserLoginSchema)
from odyssey.api.user.models import User, UserLogin
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource

# Deprecated imports, remove with deprecated endpoints
from datetime import datetime, timedelta
import secrets
import jwt

from flask import current_app, request
from odyssey.api.client_services.schemas import NewRemoteRegisterUserSchema, NewUserRegistrationPortalSchema
from odyssey.api.user.schemas import UserLoginSchema, UserSchema, UserSubscriptionsSchema
from odyssey.utils.constants import REGISTRATION_PORTAL_URL
from odyssey.utils.message import send_email_user_registration_portal
# end deprecated imports

logger = logging.getLogger(__name__)

ns = Namespace('client-services', description='Endpoints for client services operations.')


@ns.route('/account/<int:user_id>/')
class CSAccountEndpoint(BaseResource):
    """ User account info endpoint. """

    @token_auth.login_required(user_type=('staff',), staff_role=('client_services',))
    # @responds(api=ns, status_code=200)
    def get(self, user_id):
        """ Get user account info.

        Parameters
        ----------
        user_id : int
            The user_id of the **requested account**.

        Returns
        -------
        dict
            User account information.
        """
        user, user_login = db.session.execute(
            select(User, UserLogin)
            .join(
                UserLogin,
                User.user_id == UserLogin.user_id)
            .where(
                User.user_id == user_id)
        ).one_or_none()

        if not user:
            raise BadRequest(f'User {user_id} not found.')

        result = CSUserSchema().dump(user)
        result.update(CSUserLoginSchema().dump(user_login))
        return result


@ns.route('/account/<int:user_id>/block')
class CSAccountBlockEndpoint(BaseResource):
    """ Account block and unblock endpoint. """

    # Can have multiple blocks per user, 1 for client and 1 for staff
    __check_resources__ = False

    @token_auth.login_required(user_type=('staff',), staff_role=('client_services',))
    @accepts(api=ns, schema=CSAccountBlockSchema)
    @responds(api=ns, status_code=201)
    def post(self, user_id):
        """ Block a user account.

        Parameters
        ----------
        staff : bool
            Block the staff (True) or client (False) portion of the account.

        reason : str, max length 500
            Reason for the block.
        """
        user_login = (db.session.execute(
            select(UserLogin)
            .filter_by(
                user_id=user_id))
            .scalars()
            .one_or_none())

        if not user_login:
            BadRequest(f'User login information for user {user_id} not found.')

        cs_user, _ = token_auth.current_user()
        cs_id = (f'{cs_user.firstname} {cs_user.lastname} '
                 f'({cs_user.user_id}, {cs_user.modobio_id})')

        if request.json['staff']:
            user_login.staff_account_blocked = True
            user_login.staff_account_blocked_reason = request.json['reason']
            logger.audit(f'Staff account for user {user_id} blocked '
                         f'by client services member {cs_id}. Reason: ' + request.json['reason'])
        else:
            user_login.client_account_blocked = True
            user_login.client_account_blocked_reason = request.json['reason']
            logger.audit(f'Client account for user {user_id} blocked '
                         f'by client services member {cs_id}. Reason: ' + request.json['reason'])

        db.session.commit()

    @token_auth.login_required(user_type=('staff',), staff_role=('client_services',))
    @accepts(api=ns, schema=CSAccountUnblockSchema)
    @responds(api=ns, status_code=201)
    def delete(self, user_id):
        """ Remove block from a user account.

        Parameters
        ----------
        staff : bool
            Block the staff (True) or client (False) portion of the account.
        """
        user_login = (db.session.execute(
            select(UserLogin)
            .filter_by(
                user_id=user_id))
            .scalars()
            .one_or_none())

        if not user_login:
            BadRequest(f'User login information for user {user_id} not found.')

        cs_user, _ = token_auth.current_user()
        cs_id = (f'{cs_user.firstname} {cs_user.lastname} '
                 f'({cs_user.user_id}, {cs_user.modobio_id})')

        if request.json['staff']:
            user_login.staff_account_blocked = False
            user_login.staff_account_blocked_reason = None
            logger.audit(f'Staff account block for user {user_id} '
                         f'removed by client services member {cs_id}.')
        else:
            user_login.client_account_blocked = False
            user_login.client_account_blocked_reason = None
            logger.audit(f'Client account block for user {user_id} '
                         f'removed by client services member {cs_id}.')

        db.session.commit()


##################################################################
#
# Deprecated endpoints
#

@ns.deprecated
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
        """ Create new user using only email, phone number, and name.

        **Deprecated 2022-02-01**: registration portal and the ability to add accounts
        on behalf of users has not been used for a long time.

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

@ns.deprecated
@ns.route("/user/registration-portal/refresh")
class RefreshRegistrationPortal(BaseResource):
    """
    Routines related to registration portals.
    """
    @token_auth.login_required(user_type=('staff', ), staff_role=('client_services',))
    @accepts(dict(name='email', type=str), dict(name='user_type', type=str), api=ns)
    @responds(schema=NewUserRegistrationPortalSchema, api=ns, status_code=201)
    def put(self):
        """ Refresh portal ID for continued registration.

        **Deprecated 2022-02-01**: registration portal and the ability to add accounts
        on behalf of users has not been used for a long time.

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
