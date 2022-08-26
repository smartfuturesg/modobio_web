from datetime import datetime, timedelta
import logging

from flask import request
from flask_accepts import accepts, responds
from flask_restx import Namespace
from sqlalchemy import select
from werkzeug.exceptions import BadRequest

from odyssey import db
from odyssey.api.community_manager.models import CommunityManagerSubscriptionGrants
from odyssey.api.community_manager.schemas import SubscriptionGrantSchema

from odyssey.api.user.models import User, UserLogin, UserSubscriptions
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource


logger = logging.getLogger(__name__)

ns = Namespace('community-manager', description='Endpoints for community manager operations.')


@ns.route('/subscriptions/grant')
class CMSubscriptionGrantingEndpoint(BaseResource):
    """ User account info endpoint. """

    @token_auth.login_required(user_type=('staff',), staff_role=('community_manager',))
    def get(self):
        """ Returns subscriptions that have been granted by this user


        Returns
        -------
        dict
            Subscription grant history.
        """

        return 

    @accepts(api= ns, schema = SubscriptionGrantSchema)
    @token_auth.login_required(user_type=('staff',), staff_role=('community_manager',))
    def post(self):
        """ Grants subscriptions to a list of users by either modobio_id or email

        Returns
        -------
        dict
            User account information.
        """

        user, _ = token_auth.current_user()
        data = request.get_json()
        breakpoint()
        # bring up all user's that match the given email or modobio_id
        # log subscription grant request, flush for index add subscription
        grant = CommunityManagerSubscriptionGrants(user_id = user.user_id, email = data['email'], sponsor = data['sponsor'])
        db.session.add(grant)

        db.session.flush()

        subscription_end_date = datetime.utcnow() + timedelta(days=365)
        # add subscription to user
        user_sub = UserSubscriptions(user_id = user.user_id, sponsorship_id = grant.idx,
             subscription_type_id = 2, 
             subscription_status = 'subscribed', 
             expire_date = subscription_end_date, is_staff=False)

        user_sub_2 = UserSubscriptions(user_id = user.user_id, 
             subscription_status = 'subscribed', 
             expire_date = subscription_end_date, is_staff=False)

        db.session.add(user_sub)
        db.session.add(user_sub_2)
        db.session.commit()

        breakpoint()

        return


