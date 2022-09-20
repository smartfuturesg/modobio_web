import logging

from flask import current_app, request
from flask_accepts import accepts, responds
from flask_restx import Namespace
from werkzeug.exceptions import BadRequest

from odyssey import db
from odyssey.api.community_manager.models import CommunityManagerSubscriptionGrants
from odyssey.api.community_manager.schemas import PostSubscriptionGrantSchema, SubscriptionGrantsAllSchema
from odyssey.api.lookup.models import LookupSubscriptions

from odyssey.api.user.models import User
from odyssey.tasks.tasks import update_client_subscription_task
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource
from odyssey.utils.misc import update_client_subscription


logger = logging.getLogger(__name__)

ns = Namespace(
    "community-manager", description="Endpoints for community manager operations."
)


@ns.route("/subscriptions/grant")
class CMSubscriptionGrantingEndpoint(BaseResource):
    """User account info endpoint."""

    @responds(schema=SubscriptionGrantsAllSchema, api = ns)
    @token_auth.login_required(user_type=("staff",), staff_role=("community_manager",))
    def get(self):
        """Returns subscriptions that have been granted by this user

        Returns
        -------
        dict
            Subscription grant history.
        """
        user, _ = token_auth.current_user()

        subscription_grants = CommunityManagerSubscriptionGrants.query.filter_by(
            user_id=user.user_id
        ).all()

        subscription_grants_payload = []
        for subscription_grant in subscription_grants:
            if subscription_grant.subscription_grantee_user_id:
                subscription_grantee_user = User.query.filter_by(
                    user_id=subscription_grant.subscription_grantee_user_id
                ).one_or_none()
                subscription_grant.email = subscription_grantee_user.email
                subscription_grant.modobio_id = subscription_grantee_user.modobio_id

            subscription_grants_payload.append(subscription_grant.__dict__)

        payload = {"subscription_grants": subscription_grants_payload, "total_items": len(subscription_grants)}

        return payload

    @accepts(api=ns, schema=PostSubscriptionGrantSchema)
    @responds(api = ns, status_code=200)
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
        unverified_user_ids = []
        non_users = []  # emails that don't exist in the system
        
        # bring up all users that match the given email or modobio_id
        for modobio_id in data["modobio_ids"]:
            subscription_user = User.query.filter_by(
                modobio_id=modobio_id
            ).one_or_none()
            if not subscription_user:
                raise BadRequest(
                    "User with modobio_id {} does not exist".format(modobio_id)
                )
            else:
                user_ids.append(subscription_user.user_id)
                if not subscription_user.email_verified:
                    unverified_user_ids.append(subscription_user.user_id)

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
                        sponsor=data["sponsor"],
                    )
                )
            else:
                user_ids.append(subscription_user.user_id)
                if not subscription_user.email_verified:
                    unverified_user_ids.append(subscription_user.user_id)
        user_ids = list(set(user_ids))

        for user_id in user_ids:
            db.session.add(
                CommunityManagerSubscriptionGrants(
                    user_id=user.user_id,
                    sponsor=data["sponsor"],
                    subscription_grantee_user_id=user_id,
                    subscription_type_id=data["subscription_type_id"],
                )
            )

        db.session.commit()

        # update user subscriptions
        # only update subscriptions for users with a verified email
        user_ids = [uid for uid in user_ids if uid not in unverified_user_ids]
        for user_id in user_ids:
            if current_app.config['TESTING']:
                update_client_subscription(user_id)
            else:
                update_client_subscription_task.delay(user_id)
        
        db.session.commit()

        return 
