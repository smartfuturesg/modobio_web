import logging
from datetime import datetime, timedelta

from flask import current_app, request, url_for
from flask_accepts import accepts, responds
from flask_restx import Namespace
from werkzeug.exceptions import BadRequest

from odyssey import db
from odyssey.api.community_manager.models import CommunityManagerSubscriptionGrants
from odyssey.api.community_manager.schemas import (
    PostSubscriptionGrantSchema,
    ProviderLicensingSchema,
    ProviderLiscensingAllSchema,
    ProviderRoleRequestsAllSchema,
    ProviderRoleRequestUpdateSchema,
    SubscriptionGrantsAllSchema,
    VerifyMedicalCredentialSchema,
)
from odyssey.api.lookup.models import LookupSubscriptions
from odyssey.api.provider.models import ProviderCredentials, ProviderRoleRequests
from odyssey.api.staff.models import StaffRoles
from odyssey.api.user.models import User
from odyssey.tasks.tasks import update_client_subscription_task
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource
from odyssey.utils.misc import update_client_subscription

logger = logging.getLogger(__name__)

ns = Namespace(
    "community-manager",
    description="Endpoints for community manager operations.",
)


@ns.route("/subscriptions/grant")
class CMSubscriptionGrantingEndpoint(BaseResource):
    """User account info endpoint."""

    @responds(schema=SubscriptionGrantsAllSchema, api=ns)
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

        payload = {
            "subscription_grants": subscription_grants_payload,
            "total_items": len(subscription_grants),
        }

        return payload

    @accepts(api=ns, schema=PostSubscriptionGrantSchema)
    @responds(api=ns, status_code=200)
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
            if current_app.testing:
                update_client_subscription(user_id)
            else:
                update_client_subscription_task.delay(user_id, auto_renew=False)

        db.session.commit()

        return


@ns.route("/provider-licensing")
class CMProviderLicensingEndpoint(BaseResource):
    """Provider Licensing Endpoint"""

    @token_auth.login_required(user_type=("staff",), staff_role=("community_manager",))
    @responds(schema=ProviderLiscensingAllSchema, api=ns)
    @ns.doc(
        params={
            "status": "Verification Status",
            "email": "Email Address",
            "modobio_id": "Modo Bio ID",
            "start_date": "Start date range of Query",
            "end_date": "End date range of Query",
            "page": "Pagination Index",
            "per_page": "Results per page",
        }
    )
    def get(self):
        """
        Gets all medical credential licenses in the system

        Returns
            -------
            dict
                Medical Credentials Info Per User .
        """

        status = request.args.get("status", type=str)
        email = request.args.get("email", type=str)
        modobio_id = request.args.get("modobio_id", type=str)
        start_date = request.args.get("start_date", type=str)
        end_date = request.args.get("end_date", type=str)
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 100, type=int)

        query = db.session.query(ProviderCredentials, User).join(
            User, User.user_id == ProviderCredentials.user_id
        )

        # Filter and order by status
        if status:
            query = query.filter(ProviderCredentials.status == status)
            if status == "Pending Verification":
                query = query.order_by(ProviderCredentials.created_at.asc())
            if status == "Verified":
                query = query.order_by(ProviderCredentials.updated_at.asc())
            if status == "Rejected":
                query = query.order_by(ProviderCredentials.created_at.asc())
            if status == "Expired":
                query = query.order_by(ProviderCredentials.expiration_date.asc())

        # Filter by provider id
        if email:
            query = query.filter(User.email == email)
        if modobio_id:
            query = query.filter(User.modobio_id == modobio_id)

        # Convert strings to datetimes
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            if start_date > datetime.utcnow():
                raise BadRequest("Start date can not be in the future.")
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Filter query results by provided date ranges (Limited to 90 days)
        if start_date and end_date:
            if (end_date - start_date).days > 90:
                raise BadRequest("Date Range Limited to 90 Days.")
            query = query.filter(
                ProviderCredentials.created_at.between(start_date, end_date)
            )
        if start_date and not end_date:
            end_date = start_date + timedelta(days=90)
            query = query.filter(
                ProviderCredentials.created_at.between(start_date, end_date)
            )
        if end_date and not start_date:
            start_date = end_date - timedelta(days=90)
            query = query.filter(
                ProviderCredentials.created_at.between(start_date, end_date)
            )

        # Create Pagination Object
        pagination_query = query.paginate(page=page, per_page=per_page, error_out=False)
        items = pagination_query.items

        # Structure response
        result = []
        for cred, user in items:
            cred.firstname = user.firstname
            cred.lastname = user.lastname
            cred.modobio_id = user.modobio_id
            result.append(cred)

        # Remove per_page and page params from request when passing request args to links for param conflictions
        request_args = request.args.to_dict()
        request_args.pop("page", None)
        request_args.pop("per_page", None)
        return {
            "provider_licenses": result,
            "total_items": pagination_query.total,
            "_links": {
                "_prev": url_for(
                    "api.community-manager_cm_provider_licensing_endpoint",
                    page=pagination_query.prev_num,
                    per_page=per_page,
                    **request_args,
                    _external=True,
                )
                if pagination_query.has_prev
                else None,
                "_next": url_for(
                    "api.community-manager_cm_provider_licensing_endpoint",
                    page=pagination_query.next_num,
                    per_page=per_page,
                    **request_args,
                    _external=True,
                )
                if pagination_query.has_next
                else None,
            },
        }


@ns.route("/verify-credentials")
class CMVerifyCredentialsEndpoint(BaseResource):
    """Verify Medical Credentials Endpoint"""

    @token_auth.login_required(user_type=("staff",), staff_role=("community_manager",))
    @accepts(schema=VerifyMedicalCredentialSchema, api=ns)
    @responds(
        schema=ProviderLicensingSchema(exclude=("created_at", "updated_at")),
        status_code=200,
        api=ns,
    )
    def put(self):
        """
        PUT Request for updating the status for medical credentials
        """

        payload = request.json

        # Validate Status
        status = ["Verified", "Pending Verification", "Rejected", "Expired"]
        if payload["status"] not in status:
            raise BadRequest("Status must be one of {}.".format(", ".join(status)))

        query = (
            db.session.query(ProviderCredentials, User)
            .join(User, User.user_id == ProviderCredentials.user_id)
            .filter(
                ProviderCredentials.user_id == payload["user_id"],
                ProviderCredentials.idx == payload["idx"],
            )
            .one_or_none()
        )

        if query:  # query = (<ProviderCredentials>, <User>)
            query[0].update(payload)
            db.session.commit()
        else:
            raise BadRequest("Credentials not found.")

        # Include modobio id in response payload if status is markes as Rejected or Verified
        if payload["status"] == "Rejected" or payload["status"] == "Verified":
            query[0].modobio_id = query[1].modobio_id

        return query[0]


@ns.route("/provider/role-requests/")
class CMProviderRoleRequestsEndpoint(BaseResource):
    """View and update the status of provider role requests"""

    @token_auth.login_required(user_type=("staff",), staff_role=("community_manager",))
    @ns.doc(
        params={
            "page": "Pagination Index",
            "per_page": "Results per page",
            "status": "Status of role request",
        }
    )
    @responds(schema=ProviderRoleRequestsAllSchema, status_code=200, api=ns)
    def get(self):
        """
        Returns a list of all provider role requests
        """
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        status = request.args.get("status", "pending", type=str)

        # query provider role requests table join with user table
        query = (
            db.session.query(ProviderRoleRequests, User)
            .join(User, User.user_id == ProviderRoleRequests.user_id)
            .order_by(ProviderRoleRequests.created_at.asc())
        )
        if status:
            query = query.filter(ProviderRoleRequests.status == status)
        # Create Pagination Object
        pagination_query = query.paginate(page=page, per_page=per_page, error_out=False)
        items = pagination_query.items
        user_current_roles = {}
        role_requests = []
        for role_request, user in items:
            role_request.firstname = user.firstname
            role_request.lastname = user.lastname
            role_request.modobio_id = user.modobio_id
            role_request.email = user.email
            if not user_current_roles.get(user.user_id):
                user_current_roles[user.user_id] = StaffRoles.query.filter_by(
                    user_id=user.user_id
                ).all()
            role_request.current_roles = user_current_roles[user.user_id]
            role_requests.append(role_request)

        return {
            "provider_role_requests": role_requests,
            "total_items": len(role_requests),
            "_links": {
                "_prev": url_for(
                    "api.community-manager_cm_provider_role_requests_endpoint",
                    page=pagination_query.prev_num,
                    per_page=per_page,
                    status=status,
                    _external=True,
                )
                if pagination_query.has_prev
                else None,
                "_next": url_for(
                    "api.community-manager_cm_provider_role_requests_endpoint",
                    page=pagination_query.next_num,
                    per_page=per_page,
                    status=status,
                    _external=True,
                )
                if pagination_query.has_next
                else None,
            },
        }

    @token_auth.login_required(user_type=("staff",), staff_role=("community_manager",))
    @accepts(schema=ProviderRoleRequestUpdateSchema, api=ns)
    @responds(status_code=200, api=ns)
    def put(self):
        current_user, _ = token_auth.current_user()
        payload = request.json
        # validate provider role request
        provider_role_request = ProviderRoleRequests.query.filter_by(
            idx=payload.get("role_request_id")
        ).one_or_none()
        if not provider_role_request:
            raise BadRequest("Provider role request not found.")

        # validate status
        if provider_role_request.status != "pending":
            raise BadRequest(
                "Role request cannot be transitioned to accepted status from"
                f" {provider_role_request.status} status."
            )

        provider_role_request.status = payload.get("status")
        provider_role_request.reviewer_user_id = current_user.user_id

        # add new StaffRole entry for the user
        if payload.get("status") == "granted":
            staff_role = StaffRoles(
                user_id=provider_role_request.user_id,
                role=provider_role_request.role_info.role_name,
                granter_id=current_user.user_id,
                consult_rate=0,
            )
            db.session.add(staff_role)

            db.session.flush()

            # check if user has credentials linked to the role request
            provider_credentials = ProviderCredentials.query.filter_by(
                user_id=provider_role_request.user_id,
                role_request_id=provider_role_request.idx,
            ).all()
            for credential in provider_credentials:
                credential.role_id = staff_role.idx

            db.session.commit()

        else:
            # bring up the user who requested the role
            # and their current roles
            user = User.query.filter_by(
                user_id=provider_role_request.user_id
            ).one_or_none()
            user_current_roles = StaffRoles.query.filter_by(user_id=user.user_id).all()

            # if the user has no current roles and the pending role request has been rejected
            # remove their is_Provider flag from the user table
            if len(user_current_roles) == 0:
                user.is_provider = False

        db.session.commit()

        return
