import logging
logger = logging.getLogger(__name__)

from flask import request, current_app, Response
from flask_accepts import accepts, responds
from flask_restx import Namespace
from werkzeug.exceptions import BadRequest

from odyssey import db
from odyssey.api.practitioner.models import PractitionerOrganizationAffiliation
from odyssey.api.practitioner.schemas import (
    PractitionerOrganizationAffiliationSchema,
    PractitionerConsultationRateInputSchema,
)
from odyssey.api.staff.models import StaffRoles
from odyssey.api.lookup.models import LookupCurrencies, LookupOrganizations
from odyssey.utils.misc import check_staff_existence
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource

ns = Namespace('practitioner', description='Operations related to practitioners')

@ns.route('/consult-rates/<int:user_id>/')
class PractitionerConsultationRates(BaseResource):
    """
    Endpoint for practitioners to GET and SET their own HOURLY rates.
    """
    @token_auth.login_required()
    @accepts(api=ns)
    @responds(schema=PractitionerConsultationRateInputSchema,status_code=200)
    def get(self,user_id):
        """
        GET - Request to get the practitioners
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
        POST - Practitioner inputs their consultation rate
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
                if float(pract['rate'])%inc == 0:
                    lookup_role[pract['role']].update({'consult_rate':float(pract['rate'])})
                else:
                    raise InputError(status_code=405,message='Cost is not valid')
            else:
                raise InputError(status_code=405,message='Practitioner does not have selected role.')
        db.session.commit()
        return

@ns.route('/affiliations/<int:user_id>/')
class PractitionerOganizationAffiliationAPI(BaseResource):
    """
    Endpoint for Staff Admin to assign, edit and remove Practitioner's organization affiliations
    """
    # Multiple origanizations per practitioner possible
    __check_resource__ = False

    @token_auth.login_required(user_type = ('staff',), staff_role = ('staff_admin',))
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
        if True not in [role.role_info.is_practitioner for role in StaffRoles.query.filter_by(user_id=user_id).all()]:
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
