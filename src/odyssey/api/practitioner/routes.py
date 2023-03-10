import logging

from odyssey.api.user.models import User
logger = logging.getLogger(__name__)

from flask import request, current_app, Response
from flask_accepts import accepts, responds
from flask_restx import Namespace
from werkzeug.exceptions import BadRequest, Unauthorized
from sqlalchemy import select
from odyssey import db
from odyssey.api.practitioner.models import PractitionerOrganizationAffiliation, PractitionerCredentials
from odyssey.api.practitioner.schemas import (
    PractitionerOrganizationAffiliationSchema,
    PractitionerConsultationRateInputSchema,
    PractitionerCredentialsInputSchema, 
    PractitionerCredentialsSchema,
    PractitionerDeleteCredentialsSchema
)
from odyssey.api.telehealth.schemas import TelehealthStaffSettingsSchema
from odyssey.api.telehealth.models import TelehealthStaffSettings
from odyssey.api.staff.models import StaffRoles
from odyssey.api.lookup.models import LookupCurrencies, LookupOrganizations
from odyssey.utils.misc import check_staff_existence
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource

ns = Namespace('practitioner', description='Operations related to practitioners')

@ns.route('/credentials/<int:user_id>/')
@ns.deprecated
class PractionerCredentialsEndpoint(BaseResource):
    """Endpoints for getting and updating credentials. Reroutes to provider/credentials"""
    @token_auth.login_required(user_type=('staff_self',))
    @responds(schema=PractitionerCredentialsInputSchema,status_code=200,api=ns)
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
    @accepts(schema=PractitionerCredentialsInputSchema, api=ns)
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

            cred.status = 'Pending Verification'
            if current_app.debug:
                cred.status = 'Verified'
            cred.role_id = curr_role.idx
            cred.user_id = user_id
            db.session.add(cred)

        db.session.commit()
        return

    @token_auth.login_required(user_type=('staff_self',))
    @accepts(schema=PractitionerCredentialsSchema, api=ns)
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
    @accepts(schema=PractitionerDeleteCredentialsSchema,api=ns)
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
class PractitionerConsultationRates(BaseResource):
    """
    Endpoint for practitioners to GET and SET their own HOURLY rates.
    """
    @token_auth.login_required(user_type=('staff_self',))
    @accepts(api=ns)
    @responds(schema=PractitionerConsultationRateInputSchema,status_code=200)
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
    @accepts(schema=PractitionerConsultationRateInputSchema,api=ns)
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
class PractitionerOrganizationAffiliationAPI(BaseResource):
    """
    Endpoint for Staff Admin to assign, edit and remove Practitioner's organization affiliations
    """
    # Multiple origanizations per practitioner possible
    __check_resource__ = False

    @token_auth.login_required(user_type = ('staff', 'staff_self'), staff_role = ('staff_admin',))
    @responds(schema=PractitionerOrganizationAffiliationSchema(many=True), status_code=200, api=ns)
    def get(self, user_id):
        """
        Request to see the list of organizations the user_id is affiliated with
        """
        organizations = PractitionerOrganizationAffiliation.query.filter_by(user_id=user_id).all()

        for org in organizations:
            org.org_info = org.org_info

        return organizations


    @token_auth.login_required(user_type = ('staff',), staff_role = ('staff_admin',))
    @accepts(schema=PractitionerOrganizationAffiliationSchema, api=ns)
    @responds(schema=PractitionerOrganizationAffiliationSchema(many=True), status_code=201, api=ns)
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
        if True not in [role.role_info.is_provider for role in StaffRoles.query.filter_by(user_id=user_id).all()]:
            raise BadRequest('Not a practitioner.')
        
        # verify the practitioner is not already affiliated with same organization
        if data.organization_idx in [org.organization_idx for org in PractitionerOrganizationAffiliation.query.filter_by(user_id=user_id).all()]:
            raise BadRequest(
                f'Practitioner is already affiliated with organization {data.organization_idx}.')

        # Add an affiliation to PractitionerOrganizationAffiliation table
        data.user_id = user_id
        db.session.add(data)
        db.session.commit()

        organizations = PractitionerOrganizationAffiliation.query.filter_by(user_id=user_id).all()
        for org in organizations:
            org.org_info = org.org_info
        return organizations


    @token_auth.login_required(user_type = ('staff',), staff_role = ('staff_admin',))
    @responds(schema=PractitionerOrganizationAffiliationSchema(many=True), status_code=200, api=ns)
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


@ns.route('/telehealth-activation/<int:user_id>/')
class PractitionerTelehealthActivationEndpoint(BaseResource):
    """
    Activate or deactivate telehealth for providers.
    """
    @token_auth.login_required(user_type=('staff_self',))
    @responds(schema=TelehealthStaffSettingsSchema(only=['provider_telehealth_access']),status_code=200)
    def get(self, user_id):
        
        telehealth_settings = TelehealthStaffSettings.query.filter_by(user_id=user_id).one_or_none()
        if not telehealth_settings:
            #User has no telehealth settting set, therefore has no telehalth access
            return {'provider_telehealth_access': False}

        return telehealth_settings
        
    @token_auth.login_required(user_type=('staff',), staff_role=('community_manager',))
    @accepts(schema=TelehealthStaffSettingsSchema(only=['provider_telehealth_access']))
    @responds(schema=TelehealthStaffSettingsSchema(only=['provider_telehealth_access']), status_code=200)
    def put(self, user_id):
        user = self.check_user(user_id, user_type='staff')

        #update telehealth access flag
        telehalth_access_flag = request.json.get('provider_telehealth_access')
        telehealth_settings = TelehealthStaffSettings.query.filter_by(user_id=user.user_id).one_or_none()
        if not telehealth_settings:
            #Create telehealth settings with default values and provided flag
            telehealth_settings = TelehealthStaffSettings(
                user_id=user.user_id, provider_telehealth_access=telehalth_access_flag
                )
            db.session.add(telehealth_settings)
        else:
            telehealth_settings.provider_telehealth_access = telehalth_access_flag
        db.session.commit()

        return telehealth_settings