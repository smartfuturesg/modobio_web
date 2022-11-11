
import logging

from datetime import time, datetime, timedelta

from flask import current_app, request
from flask_accepts import accepts, responds
from flask_restx import Namespace
from werkzeug.exceptions import BadRequest, Unauthorized
from sqlalchemy import select

from odyssey import db
from odyssey.api.lookup.models import (
    LookupTerritoriesOfOperations,
    LookupCountriesOfOperations,
    LookupRoles,
    LookupOrganizations,
    LookupCurrencies)
from odyssey.api.provider.schemas import *
from odyssey.api.provider.models import *
from odyssey.api.staff.models import (
    StaffOperationalTerritories,
    StaffRoles,
    StaffRecentClients,
    StaffProfile,
    StaffCalendarEvents,
    StaffOffices)
from odyssey.api.staff.schemas import StaffTokenRequestSchema
from odyssey.api.user.models import (
    User,
    UserLogin,
    UserTokenHistory,
    UserProfilePictures)
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
@ns.route('/credentials/<int:user_id>/')
class ProviderCredentialsEndpoint(BaseResource):
    """Endpoints for getting and updating credentials. Reroutes to provider/credentials"""
    @token_auth.login_required(user_type=('staff_self',))
    @responds(schema=ProviderCredentialsInputSchema,status_code=200,api=ns)
    def get(self, user_id):
        """
        GET Request for Pulling Medical Credentials for a practitioner

        User should be client
        """

        if not user_id:
            raise BadRequest('Missing User ID.')

        current_user, _ = token_auth.current_user()
        if current_user.user_id != user_id:
            raise Unauthorized()

        query = db.session.execute(
            select(PractitionerCredentials).
            where(
                PractitionerCredentials.user_id == user_id
                )
        ).scalars().all()
        return {'items': query}

    @token_auth.login_required(user_type=('staff_self',))
    @accepts(schema=ProviderCredentialsInputSchema, api=ns)
    @responds(status_code=201,api=ns)
    def post(self, user_id):
        """
        POST Request for submitting Medical Credentials for a practitioner

        User should be Staff Self
        """

        if not user_id:
            raise BadRequest('Missing User ID.')

        current_user, _ = token_auth.current_user()
        if current_user.user_id != user_id:
            raise Unauthorized()

        payload = request.parsed_obj
        state_check = {}
        for role, cred in payload['items']:

            curr_role = StaffRoles.query.filter_by(user_id=user_id,role=role).one_or_none()
            # This takes care of ensuring credential number is submitted if user
            # submits a payload with a state for DEA and Medical License credential types
            if (cred.credential_type != 'npi' and cred.state) and not cred.credentials:
                raise BadRequest('Credential number is mandatory if submitting with a state.')

            # This takes care of only allowing 1 state input per credential type
            # Example:
            # (Good) DEA - AZ, CA
            # (Bad)  DEA - AZ, AZ
            if cred.credential_type not in state_check:
                state_check[cred.credential_type]=[]
                state_check[cred.credential_type].append(cred.state)
            else:
                if cred.state in state_check[cred.credential_type]:
                    # Rollback is necessary because we applied database changes above
                    db.session.rollback()
                    raise BadRequest(f'Multiple {cred.state} submissions for {cred.credential_type}. '
                                     f'Only one credential per state is allowed')
                else:
                    state_check[cred.credential_type].append(cred.state)

            cred.status = 'Pending Verification' if not any([current_app.config['DEV'],current_app.config['TESTING']]) else 'Verified'
            cred.role_id = curr_role.idx
            cred.user_id = user_id
            db.session.add(cred)

        db.session.commit()
        return

    @token_auth.login_required(user_type=('staff_self',))
    @accepts(schema=ProviderCredentialsSchema, api=ns)
    @responds(status_code=201,api=ns)
    def put(self, user_id):
        """
        PUT Request for updating the status for medical credentials

        User for this request should be the Staff Admin
        """

        if not user_id:
            raise BadRequest('Missing User ID.')

        current_user, _ = token_auth.current_user()
        if current_user.user_id != user_id:
            raise Unauthorized()
        
        valid_statuses = ['Rejected', 'Expired']

        payload = request.json
        payload.pop('staff_role') # Staff_role passed in schema but isn't part of PractitionerCredentials model
        
        curr_credentials = PractitionerCredentials.query.filter_by(user_id=user_id,idx=payload['idx']).one_or_none()
        if curr_credentials.status not in valid_statuses:
            raise BadRequest('Current credential status must be rejected or expired.')

        if curr_credentials:
            payload['status'] = 'Pending Verification'
            curr_credentials.update(payload)
            db.session.commit()
        else:
            raise BadRequest('Credentials not found.')
        return

    @token_auth.login_required(user_type=('staff_self',))
    @accepts(schema=ProviderDeleteCredentialsSchema,api=ns)
    @responds(status_code=201,api=ns)
    def delete(self, user_id):
        """
        DELETE Request for deleting medical credentials

        User for this request should be the Staff Self and Staff Admin
        """
        if not user_id:
            raise BadRequest('Missing User ID.')
                
        current_user, _ = token_auth.current_user()
        if current_user.user_id != user_id:
            raise Unauthorized()

        payload = request.json

        curr_credentials = PractitionerCredentials.query.filter_by(user_id=user_id,idx=payload['idx']).one_or_none()

        if curr_credentials:
            db.session.delete(curr_credentials)
            db.session.commit()
        else:
            raise BadRequest('Credentials not found.')
        return


@ns.route('/consult-rates/<int:user_id>/')
class ProviderConsultationRates(BaseResource):
    """
    Endpoint for practitioners to GET and SET their own HOURLY rates.
    """
    @token_auth.login_required(user_type=('staff_self',))
    @accepts(api=ns)
    @responds(schema=ProviderConsultationRateInputSchema,status_code=200)
    def get(self,user_id):
        """
        Responds with all roles and consultation rates for provider
        """
        staff_user_roles = db.session.query(StaffRoles).filter(StaffRoles.user_id==user_id).all()

        items = []
        for role in staff_user_roles:
            items.append({'role': role.role,'rate': str(role.consult_rate)})

        return {'items': items}
    
    @token_auth.login_required(user_type = ('staff_self',))
    @accepts(schema=ProviderConsultationRateInputSchema,api=ns)
    @responds(status_code=201)
    def post(self,user_id):
        """
        Provider submits consultation rates for each role
        """
        # grab all of the roles the practitioner may have
        staff_user_roles = db.session.query(StaffRoles).filter(StaffRoles.user_id==user_id).all()
        
        payload = request.json
        
        lookup_role = {}
        for roleObj in staff_user_roles:
            if roleObj.role not in lookup_role:
                lookup_role[roleObj.role] = roleObj

        cost_range = LookupCurrencies.query.one_or_none()
        inc = cost_range.increment
        
        for pract in payload['items']:
            if pract['role'] in lookup_role:
                if float(pract['rate']) < float(cost_range.min_rate) or float(pract['rate']) > float(cost_range.max_rate):
                    raise BadRequest(f'Input must be between {cost_range.min_rate} and {cost_range.max_rate}.')
                if float(pract['rate'])%inc == 0.0:
                    lookup_role[pract['role']].update({'consult_rate':float(pract['rate'])})
                else:
                    raise BadRequest('Cost is not valid')
            else:
                raise BadRequest('Practitioner does not have selected role.')

        db.session.commit()
        return

@ns.route('/affiliations/<int:user_id>/')
class ProviderOganizationAffiliationAPI(BaseResource):
    """
    Endpoint for Staff Admin to assign, edit and remove Practitioner's organization affiliations
    """
    # Multiple organizations per practitioner possible
    __check_resource__ = False

    @token_auth.login_required(user_type = ('staff', 'staff_self'), staff_role = ('staff_admin',))
    @responds(schema=ProviderOrganizationAffiliationSchema(many=True), status_code=200, api=ns)
    def get(self, user_id):
        """
        Request to see the list of organizations the user_id is affiliated with
        """
        organizations = PractitionerOrganizationAffiliation.query.filter_by(user_id=user_id).all()

        for org in organizations:
            org.org_info = org.org_info

        return organizations


    @token_auth.login_required(user_type = ('staff',), staff_role = ('staff_admin',))
    @accepts(schema=ProviderOrganizationAffiliationSchema, api=ns)
    @responds(schema=ProviderOrganizationAffiliationSchema(many=True), status_code=201, api=ns)
    def post(self, user_id):
        """
        Request to add an organization the user_id is affiliated with
        """
        data = request.parsed_obj
        
        # validate organization_id 
        organizations = [org.idx for org in LookupOrganizations.query.all()]
        if data.organization_idx not in organizations:
            raise BadRequest('Invalid organization.')
        
        # verify user_id has a practitioner role (will also raise error if user_id doesn't exist or is client)
        if True not in [role.role_info.is_practitioner for role in StaffRoles.query.filter_by(user_id=user_id).all()]:
            raise BadRequest('Not a practitioner.')
        
        # verify the practitioner is not already affiliated with same organization
        if data.organization_idx in [org.organization_idx for org in PractitionerOrganizationAffiliation.query.filter_by(user_id=user_id).all()]:
            raise BadRequest(
                f'Provider is already affiliated with organization {data.organization_idx}.')

        # Add an affiliation to PractitionerOrganizationAffiliation table
        data.user_id = user_id
        db.session.add(data)
        db.session.commit()

        organizations = PractitionerOrganizationAffiliation.query.filter_by(user_id=user_id).all()
        for org in organizations:
            org.org_info = org.org_info
        return organizations


    @token_auth.login_required(user_type = ('staff',), staff_role = ('staff_admin',))
    @responds(schema=ProviderOrganizationAffiliationSchema(many=True), status_code=200, api=ns)
    @ns.doc(params={'organization_idx': '(Optional) Index of organization to remove affiliation with'})
    def delete(self, user_id):
        """
        Request to remove one or all organizations the user_id is affiliated with

        If a value is provided with param key 'organization_idx', only such affiliation will be removed
        Otherwise, all affiliations for the user_id will be removed.
        """
        
        if 'organization_idx' in request.args:
            # validate organization_idx is a valid integer, if it was provided at all 
            if not request.args['organization_idx'].isnumeric():
                raise BadRequest('Organization_idx must be a positive integer.')

            # if organization_idx is valid int delete that affiliation, 
            # if the idx doesn't exist, nothing will happen
            PractitionerOrganizationAffiliation.query.\
                filter_by(user_id=user_id, organization_idx=request.args['organization_idx']).delete()
            
        else:
            #delete all affiliations
            PractitionerOrganizationAffiliation.query.filter_by(user_id=user_id).delete()
        
        # nothing will be removed if the organization index provided doesn't exist
        db.session.commit()

        # return all affiliations left on db
        organizations = PractitionerOrganizationAffiliation.query.filter_by(user_id=user_id).all()
        for org in organizations:
            org.org_info = org.org_info
        return organizations

@ns.route('/role/requests/<int:user_id>/')
class ProviderRoleRequestsEndpoint(BaseResource):
    """
    Endpoint for submitting, removing, and retrieving requests for provider roles

    Provider roles are those found in the LookupRoles table and are marked as is_provider = True
    """
    # Multiple organizations per practitioner possible
    __check_resource__ = False

    @token_auth.login_required(user_type = ('client', 'staff_self',))
    @responds(schema=ProviderRoleRequestsAllSchema, status_code=200, api=ns)
    def get(self, user_id):
        """
        View current role requests. Only one ongoing role request is active at a time. 

        Active role requests are those with a status listed as pending. All other role 
        requests are considered completed (rejected, granted) or inactive.

        Returns
        ------- 
        dict with all role request details for the user_id specified
        """

        # TODO
        # bring up role requests for user_id
        # place list in schema and return

        role_requests = ProviderRoleRequests.query.filter_by(user_id=user_id).all()

        payload = {'items': role_requests, 'total_items': len(role_requests)} 

        return payload

    @token_auth.login_required(user_type = ('client', 'staff_self'))
    @ns.doc(params={'role_id': 'Index of role to request from LookupRoles.idx'})
    @responds(schema=ProviderRoleRequestsAllSchema, status_code=201, api=ns)
    def post(self, user_id):
        """
        Make a request for a provider role. If the user is not currently a provider, this endpoint
        will grant provider login to the user. 

        Role requests are considered pending until all required information is provided and request is
        reviewed by a staff member. 
        
        """
        user, _ = token_auth.current_user()
        # validate role_id. Must be a provider role
        requested_role = LookupRoles.query.filter_by(idx=request.args['role_id']).first()

        if not requested_role.is_provider:
            raise BadRequest('Requested role is not intended for providers.')

        # check if there are any other pending role requests for the user_id
        if ProviderRoleRequests.query.filter_by(user_id=user_id, status='pending').first():
            raise BadRequest('There is already an active role request for this user.')

        # grant user provider login privileges if they don't have them already
        if not user.is_provider:
            user.is_provider = True
            db.session.flush()
        
        # create a new role request
        role_request = ProviderRoleRequests(user_id=user_id, role_id=request.args['role_id'], status='pending')
        db.session.add(role_request)

        db.session.commit()
        # return role requests for user_id
        payload = {'items': [role_request], 'total_items': 1}

        return payload


    @token_auth.login_required(user_type = ('client', 'staff_self'))
    @ns.doc(params={'request_id': 'Index of role request from LookupRoles.idx'})
    @responds(schema=ProviderRoleRequestsAllSchema, status_code=200, api=ns)
    def put(self, user_id):
        """
        Update the status of a role request to inactive. This will remove the role request
        from the review process.
        """
        # bring up the role request 
        role_request = ProviderRoleRequests.query.filter_by(user_id = user_id, idx=request.args['request_id']).one_or_none()
        if not role_request:
            raise BadRequest('Role request does not exist.')

        if role_request.status not in ('pending', 'inactive', 'rejected'):
            raise BadRequest('Role request status cannot be changed')

        role_request.status = 'inactive'
        db.session.commit()

        return

        