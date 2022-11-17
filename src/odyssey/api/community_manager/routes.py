from datetime import datetime, timedelta
import logging

from flask import current_app, request, url_for
from flask_accepts import accepts, responds
from flask_restx import Namespace
from werkzeug.exceptions import BadRequest

from odyssey import db
from odyssey.api.community_manager.models import CommunityManagerSubscriptionGrants
from odyssey.api.community_manager.schemas import (
    PostSubscriptionGrantSchema, 
    ProviderLiscensingAllSchema, 
    VerifyMedicalCredentialSchema, 
    SubscriptionGrantsAllSchema, 
    ProviderLicensingSchema
)
from odyssey.api.lookup.models import LookupSubscriptions

from odyssey.api.user.models import User
from odyssey.api.practitioner.models import PractitionerCredentials
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

@ns.route("/provider-licensing")
class CMProviderLicensingEndpoint(BaseResource):
    """Provider Licensing Endpoint"""
    
    @token_auth.login_required(user_type=("staff",), staff_role=("community_manager",))
    @responds(schema=ProviderLiscensingAllSchema, api=ns)
    @ns.doc(params={'status': 'Verification Status',
                    'email': 'Email Address',
                    'modobio_id': 'Modo Bio ID',
                    'start_date': 'Start date range of Query', 
                    'end_date': 'End date range of Query', 
                    'page': 'Pagination Index', 
                    'per_page': 'Results per page'
    })
    def get(self):
        """
        Gets all medical credential licenses in the system

        Returns
            -------
            dict
                Medical Credentials Info Per User .
        """

        status = request.args.get('status', type=str)
        email = request.args.get('email', type=str)
        modobio_id = request.args.get('modobio_id', type=str)
        start_date = request.args.get('start_date', type=str)
        end_date = request.args.get('end_date', type=str)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)

        query = db.session.query(PractitionerCredentials, User)\
            .join(User, User.user_id == PractitionerCredentials.user_id)

        #Filter and order by status
        if status:
            query = query.filter(PractitionerCredentials.status == status)
            if status == 'Pending Verification':
                query = query.order_by(PractitionerCredentials.created_at.asc())
            if status == 'Verified':
                query = query.order_by(PractitionerCredentials.updated_at.asc())
            if status == 'Rejected':
                query = query.order_by(PractitionerCredentials.created_at.asc())
            if status == 'Expired':
                query = query.order_by(PractitionerCredentials.expiration_date.asc())
                
        #Filter by provider id 
        if email:
            query = query.filter(User.email == email)
        if modobio_id:
            query = query.filter(User.modobio_id == modobio_id)
        
        # Convert strings to datetimes
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            if start_date > datetime.utcnow():
                raise BadRequest('Start date can not be in the future.')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        #Filter query results by provided date ranges (Limited to 90 days)
        if start_date and end_date:
            if (end_date - start_date).days > 90:
                raise BadRequest('Date Range Limited to 90 Days.')
            query = query.filter(PractitionerCredentials.created_at.between(start_date, end_date))
        if start_date and not end_date:
            end_date = start_date + timedelta(days=90)
            query = query.filter(PractitionerCredentials.created_at.between(start_date, end_date))
        if end_date and not start_date:
            start_date = end_date - timedelta(days=90)
            query = query.filter(PractitionerCredentials.created_at.between(start_date, end_date))

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
        
        #Remove per_page and page params from request when passing request args to links for param conflictions 
        request_args = request.args.to_dict() 
        request_args.pop('page', None)
        request_args.pop('per_page', None)
        return {
            'provider_licenses': result, 
            'total_items': pagination_query.total,
            '_links': {
                '_prev': url_for('api.community-manager_cm_provider_licensing_endpoint', 
                    page=pagination_query.prev_num, per_page = per_page, **request_args, _external=True
                    ) if pagination_query.has_prev else None,
                '_next': url_for('api.community-manager_cm_provider_licensing_endpoint', 
                    page=pagination_query.next_num, per_page = per_page, **request_args, _external=True
                    ) if pagination_query.has_next else None,
                }
            }

@ns.route("/verify-credentials")
class CMVerifyCredentialsEndpoint(BaseResource):
    """Verify Medical Credentials Endpoint"""

    @token_auth.login_required(user_type=("staff",), staff_role=("community_manager",))
    @accepts(schema=VerifyMedicalCredentialSchema, api=ns)
    @responds(schema=ProviderLicensingSchema(exclude=('created_at', 'updated_at')), status_code=200,api=ns)
    def put(self):
        """
        PUT Request for updating the status for medical credentials
        """

        payload = request.json
        
        #Validate Status
        status = ['Verified','Pending Verification', 'Rejected', 'Expired']
        if payload['status'] not in status:
            raise BadRequest('Status must be one of {}.'.format(', '.join(status)))

        query = db.session.query(PractitionerCredentials, User)\
            .join(User, User.user_id == PractitionerCredentials.user_id).\
                filter(PractitionerCredentials.user_id==payload['user_id']\
                    ,PractitionerCredentials.idx==payload['idx']).one_or_none()

        if query: #query = (<PractitionerCredentials>, <User>)
            query[0].update(payload)
            db.session.commit()
        else:
            raise BadRequest('Credentials not found.')

        #Include modobio id in response payload if status is markes as Rejected or Verified
        if payload['status'] == 'Rejected' or payload['status'] == 'Verified':
            query[0].modobio_id = query[1].modobio_id

        return query[0]