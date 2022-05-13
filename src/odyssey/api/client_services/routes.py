import logging

from flask import request
from flask_accepts import accepts, responds
from flask_restx import Namespace
from sqlalchemy import select
from werkzeug.exceptions import BadRequest

from odyssey import db
from odyssey.api.client_services.schemas import (
    CSAccountBlockSchema,
    CSAccountUnblockSchema,
    CSUserSchema,
    CSUserLoginSchema)
from odyssey.api.user.models import User, UserLogin
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource

from flask import request

logger = logging.getLogger(__name__)

ns = Namespace('client-services', description='Endpoints for client services operations.')


@ns.route('/account/<int:user_id>/')
class CSAccountEndpoint(BaseResource):
    """ User account info endpoint. """

    @token_auth.login_required(user_type=('staff',), staff_role=('client_services',))
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

