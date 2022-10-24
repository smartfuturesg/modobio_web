
import logging

from datetime import time, datetime, timedelta

from flask import request
from flask_accepts import accepts, responds
from flask_restx import Namespace
from werkzeug.exceptions import BadRequest, Unauthorized

from odyssey import db
from odyssey.api.lookup.models import (
    LookupTerritoriesOfOperations,
    LookupCountriesOfOperations,
    LookupRoles)
from odyssey.api.staff.models import (
    StaffOperationalTerritories,
    StaffRoles,
    StaffRecentClients,
    StaffProfile,
    StaffCalendarEvents,
    StaffOffices)
from odyssey.api.staff.schemas import (
    StaffOperationalTerritoriesNestedSchema,
    StaffProfileSchema, 
    StaffRolesSchema,
    StaffRecentClientsSchema,
    StaffTokenRequestSchema,
    StaffInternalRolesSchema)
from odyssey.api.user.models import (
    User,
    UserLogin,
    UserTokenHistory,
    UserProfilePictures)
from odyssey.api.user.routes import UserLogoutApi
from odyssey.api.user.schemas import UserSchema
from odyssey.utils.auth import token_auth, basic_auth
from odyssey.utils.base.resources import BaseResource
from odyssey.utils.constants import MIN_CUSTOM_REFRESH_TOKEN_LIFETIME, MAX_CUSTOM_REFRESH_TOKEN_LIFETIME

from odyssey.api.staff.schemas import StaffTokenRequestSchema
from odyssey.utils.base.resources import BaseResource

logger = logging.getLogger(__name__)

ns = Namespace('provider', description='Operations related to providers')

@ns.route('/token/')
class ProviderToken(BaseResource):
    """create and revoke tokens"""
    @ns.doc(security='password', params={'refresh_token_lifetime': 'Lifetime for staff refresh token'})
    @basic_auth.login_required(user_type=('provider',), email_required=False)
    @responds(schema=StaffTokenRequestSchema, status_code=201, api=ns)
    def post(self):
        """generates a token for the 'current_user' immediately after password authentication"""
        user, user_login = basic_auth.current_user()

        if not user:
            raise Unauthorized

        # bring up list of staff roles
        access_roles = db.session.query(
                                StaffRoles.role
                            ).filter(
                                StaffRoles.user_id==user.user_id
                            ).all()

        refresh_token_lifetime = request.args.get('refresh_token_lifetime', type=int)

        # Handle refresh token lifetime param
        if refresh_token_lifetime:
            # Convert lifetime from days to hours
            if MIN_CUSTOM_REFRESH_TOKEN_LIFETIME <= refresh_token_lifetime <= MAX_CUSTOM_REFRESH_TOKEN_LIFETIME:
                refresh_token_lifetime *= 24
            # Else lifetime is not in acceptable range
            else:
                raise BadRequest('Custom refresh token lifetime must be between 1 and 30 days.')

        access_token = UserLogin.generate_token(user_type='provider', user_id=user.user_id, token_type='access')
        refresh_token = UserLogin.generate_token(user_type='provider', user_id=user.user_id, token_type='refresh', refresh_token_lifetime=refresh_token_lifetime)

        db.session.add(UserTokenHistory(user_id=user.user_id, 
                                        refresh_token=refresh_token,
                                        event='login',
                                        ua_string = request.headers.get('User-Agent')))

        # If a user logs in after closing the account, but within the account
        # deletion limit, the account will be reopened and not deleted.
        if user_login.staff_account_closed:
            user_login.staff_account_closed = None
            user_login.staff_account_closed_reason = None

        db.session.commit()

        return {'email': user.email, 
                'firstname': user.firstname, 
                'lastname': user.lastname, 
                'token': access_token,
                'refresh_token': refresh_token,
                'user_id': user.user_id,
                'access_roles': [item[0] for item in access_roles],
                'email_verified': user.email_verified}
