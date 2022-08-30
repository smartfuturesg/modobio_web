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
from odyssey.api.lookup.models import LookupSubscriptions

from odyssey.api.user.models import User, UserLogin, UserSubscriptions
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource


logger = logging.getLogger(__name__)

ns = Namespace(
    "community-manager", description="Endpoints for community manager operations."
)


@ns.route("/subscriptions/grant")
class CMSubscriptionGrantingEndpoint(BaseResource):
    """User account info endpoint."""

    @token_auth.login_required(user_type=("staff",), staff_role=("community_manager",))
    def get(self):
        """Returns subscriptions that have been granted by this user


        Returns
        -------
        dict
            Subscription grant history.
        """

        return

    @accepts(api=ns, schema=SubscriptionGrantSchema)
    @token_auth.login_required(user_type=("staff",), staff_role=("community_manager",))
    def post(self):
        """Grants subscriptions to a list of users by either modobio_id or email

        Returns
        -------
        dict
            User account information.
        """

        user, _ = token_auth.current_user()
        data = request.parsed_obj

        # validate subscription type
        subscription_type = LookupSubscriptions.query.filter_by(
            sub_id=data["subscription_type_id"]
        ).one_or_none()

        if not subscription_type:
            raise BadRequest("Invalid subscription type")

        user_ids = []
        non_users = []  # emails that don't exist in the system

        # bring up all user's that match the given email or modobio_id
        for modobio_id in data["modobio_ids"]:
            subscription_user = User.query.filter_by(
                modobio_id=modobio_id
            ).one_or_none()
            if not subscription_user:
                raise BadRequest(
                    "User with modobio_id {} does not exist".format(modobio_id)
                )
            user_ids.append(subscription_user.user_id)

        # bring up users by email
        # if email not associated with an account, store the email in another list
        for email in data["emails"]:
            subscription_user = User.query.filter_by(email=email.lower()).one_or_none()
            if not subscription_user:
                # store subscription grant info under the user's email for future use
                non_users.append(email)
                db.session.add(
                    CommunityManagerSubscriptionGrants(
                        user_id=user.user_id,
                        email=email,
                        subscription_type_id=data["subscription_type_id"],
                    )
                )
            else:
                user_ids.append(subscription_user.user_id)

        user_ids = list(set(user_ids))

        subscription_grants = []
        for user_id in user_ids:
            subscription_grants.append(
                CommunityManagerSubscriptionGrants(
                    user_id=user.user_id,
                    sponsor=user.modobio_id,
                    subscription_grantee_user_id=user_id,
                    subscription_type_id=data["subscription_type_id"],
                )
            )

        db.session.add_all(subscription_grants)
        db.session.flush()

        # add subscription details to the user's subscriptions table
        # check the current subscription status of the user
        # if the user is not subscribed, add the subscription
        # if the user is subscribed, check if the subscription is expired

        # Cases
        # 1. No currently active subscription
        #   make entry to UserSubscriptions with appropriate expire date
        # 2. Current subscription with Apple/Android
        #   Do nothing. The subscription grant will be checked upon renewal
        # 3. Current subscription granted through the subscription granting scheme
        #   Do nothing. Subscription grant checked on renewal in background
                # Update the previous subscription if necessary

        
        prev_sub = UserSubscriptions.query.filter_by(user_id=user_id, ).order_by(UserSubscriptions.idx.desc()).first()

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
    

        breakpoint()
        subscription_end_date = datetime.utcnow() + timedelta(days=365)
        # add subscription to user
        user_sub = UserSubscriptions(
            user_id=user.user_id,
            sponsorship_id=grant.idx,
            subscription_type_id=2,
            subscription_status="subscribed",
            expire_date=subscription_end_date,
            is_staff=False,
        )

        user_sub_2 = UserSubscriptions(
            user_id=user.user_id,
            subscription_status="subscribed",
            expire_date=subscription_end_date,
            is_staff=False,
        )

        db.session.add(user_sub)
        db.session.add(user_sub_2)
        db.session.commit()

        breakpoint()

        return
