import requests
from datetime import datetime

from flask import g, request, current_app
from flask_accepts import accepts, responds
from flask.json import dumps
from flask_restx import Resource, Namespace
from sqlalchemy import select
from werkzeug.exceptions import BadRequest

from odyssey import db

from odyssey.api.dosespot.models import (
    DoseSpotPractitionerID,
    DoseSpotPatientID,
    DoseSpotProxyID
)
from odyssey.api.dosespot.schemas import (
    DoseSpotPrescribeSSO,
    DoseSpotPharmacyNestedSelect,
    DoseSpotEnrollmentGET,
    DoseSpotAllergyOutput,
    DoseSpotPrescribedOutput
)
from odyssey.api.lookup.models import (
    LookupTerritoriesOfOperations,
)

from odyssey.api.notifications.models import Notifications

from odyssey.api.user.models import User
from odyssey.integrations.dosespot import DoseSpot
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource
from odyssey.utils.dosespot import (
    generate_encrypted_user_id,
    get_access_token,
    lookup_ds_users,
    onboard_patient
)

ns = Namespace('dosespot', description='Operations related to DoseSpot')

@ns.route('/allergies/<int:user_id>/')
class DoseSpotAllergies(BaseResource):
    @token_auth.login_required(user_type=('staff','client'),staff_role=('medical_doctor',))
    @responds(schema=DoseSpotAllergyOutput,status_code=200,api=ns)
    def get(self, user_id):
        """
        Bring up the client's allergies to medications stored on DoseSpot
        """
        ds_patient = DoseSpotPatientID.query.filter_by(user_id=user_id).one_or_none()
        ds = DoseSpot()
        if not ds_patient:
            ds_patient = ds.onboard_client(user_id)

        ds_allergies = ds.allergies(user_id)
        
        payload = {'items': ds_allergies['Items'],
                   'total_items': len(ds_allergies['Items'])}

        return payload

@ns.route('/create-practitioner/<int:user_id>/')
class DoseSpotPractitionerCreation(BaseResource):
    @token_auth.login_required(user_type=('staff',),staff_role=('medical_doctor',))
    @responds(status_code=201, api=ns)
    def post(self, user_id):
        """
        POST - Only a DoseSpot Admin will be able to use this endpoint. As a workaround
               we have stored a DoseSpot Admin credentials so the ModoBio system will be able
               to create the practitioner on the DoseSpot platform
        """
        ds = DoseSpot()
        ds.onboard_practitioner(user_id)
        db.session.commit()
        return 

@ns.route('/prescribe/<int:user_id>/')
class DoseSpotPatientCreation(BaseResource):
    @token_auth.login_required(user_type=('staff','client'),staff_role=('medical_doctor',))
    @responds(schema=DoseSpotPrescribedOutput,status_code=200,api=ns)
    def get(self, user_id):
        """
        Returns the client's prescriptions that have been prescribed through DoseSpot. Both client and medical doctor practitioners have access 
        to this endpoint. 

        Params
        ------
        user_id: int
            user_id for the client
        """
        ds = DoseSpot()
        prescriptions = ds.prescriptions(user_id)

        payload = {'items': prescriptions['Items'],
                   'total_items': len(prescriptions['Items'])}

        return payload

    @token_auth.login_required(user_type=('staff',),staff_role=('medical_doctor',))      
    @responds(schema=DoseSpotPrescribeSSO,status_code=201,api=ns)
    def post(self, user_id):
        """
        Generate an SSO directed at the prescribing page on the DoseSpot platform. Only practitioners with the medical_doctor role will 
        have access to this endpoint. 
        TODO: restrict this endpoint to practitioners given care team access to the user in the path parameter

        Params
        ------
        user_id: int
            user_id for the client
        
        Returns
        ------
        url: str
            SSO to the DoseSpot prescribing portal
        """
        curr_user,_ = token_auth.current_user()

        ds = DoseSpot(practitioner_user_id = curr_user.user_id)
        
        return {'url': ds.prescribe(client_user_id = user_id)}

@ns.route('/notifications/<int:user_id>/')
class DoseSpotNotificationSSO(BaseResource):
    @token_auth.login_required(user_type=('staff',),staff_role=('medical_doctor',))
    @responds(schema=DoseSpotPrescribeSSO,status_code=200, api=ns)
    def get(self, user_id):
        """
        Bring up DoseSpot notifications for the practitioner. Stores notification count as a notification 
        entry on the modobio platform. Responds with SSO to access notification content on DoseSpot. 

        Params
        ------
        user_id: int
            Must be a practitioner registered with DoseSpot
        
        Returns
        ------
        url: str
            SSO which sends user directly to their notifications
        """
        ds = DoseSpot(practitioner_user_id = user_id)
        url = ds.notifications()

        return {'url': url}

@ns.route('/enrollment-status/<int:user_id>/')
@ns.doc(params={'user_type': '\'client\' or \'staff\'. defaults to staff'})
class DoseSpotEnrollmentStatus(BaseResource):
    @token_auth.login_required(user_type=('staff','client'),staff_role=('medical_doctor',))
    @responds(schema=DoseSpotEnrollmentGET,status_code=200, api=ns)
    def get(self, user_id):
        """
        Returns the DoseSpot enrollment status for the provided user_id. Responds in error if the user is not enrolled at all. 

        Params
        ------
        user_id: int
            Must be a practitioner registered with DoseSpot
        
        Returns
        ------
        enrollment status: str
            'enrolled', 'pending', 'not enrolled' (client only) 
        """
        ds = DoseSpot()
        utype = request.args.get('user_type', 'staff', type = str)
        return {'status':ds.enrollment_status(user_id, user_type = utype)}

@ns.route('/select/pharmacies/<int:user_id>/')
@ns.doc(params = {'zipcode': '(optional) overrides user\'s zipcode', 
            'state_id': '(optional) overrides user\'s state'})
class DoseSpotSelectPharmacies(BaseResource):
    @token_auth.login_required(user_type=('client',))
    def get(self,user_id):
        """
        Queries DoseSpot for a list of available pharmacies. By default this endpoint uses the client's address
        to locate pharmacies. Optionally a user may submit a zipcode and state_id 

        Params
        ------
        user_id: int
        zipcode: str
            Optional zipcode for pharmacy search
        state_id: int
            Optional state_id from LookupTerritoriesOfOperations

        Returns
        ------
        pharmacies: [dict]
            big list of pharmacies
        """
        zipcode = request.args.get('zipcode', None)
        state_id = request.args.get('state_id', None)

        # if no zopcode not state specified, use client's address detail by default
        if not zipcode and not state_id:
            user = User.query.filter_by(user_id = user_id).one_or_none()
            zipcode = user.client_info.zipcode
            state_id = user.client_info.territory_id
        
        ds = DoseSpot()

        pharmacies = ds.pharmacy_search(state_id = state_id, zipcode = zipcode)
        
        return pharmacies['Items']

@ns.route('/pharmacies/<int:user_id>/')
class DoseSpotPatientPharmacies(BaseResource):
    @token_auth.login_required(user_type=('client',))
    def get(self, user_id):
        """
        Retrieve from DoseSpot the pharmacies the Modobio client has selected (at most 3.)
        Params
        ------
        user_id: int

        Returns
        ------
        pharamacies: [dict]
            list of up to 3 pharmacies
        """
        
        ds = DoseSpot()
        pharmacies = ds.client_pharmacies(user_id)
        
        return pharmacies['Items']

    @token_auth.login_required(user_type=('client',))
    @accepts(schema=DoseSpotPharmacyNestedSelect,api=ns)
    @responds(status_code=201,api=ns)
    def post(self, user_id):
        """
        POST - The pharmacies the Modobio client has selected (at most 3.)
               We delete the existing pharmacy selection, and populate with the selected choices
               DoseSpot Admin credentials will be used for this endpoint
        """
        payload = request.json
        if len(payload['items'])>3:
            raise BadRequest('Can only select up to 3 pharmacies.')

        primary_pharm_count = 0
        for item in payload['items']:
            if item['primary_pharm']:
                primary_pharm_count+=1
            if primary_pharm_count > 1:
                raise BadRequest('Must select only 1 pharmacy to be set as primary.')
        if primary_pharm_count == 0:
            raise BadRequest('Must select 1 pharmacy to be set as primary.')

        # # DoseSpotPatientID
        ds_patient = DoseSpotPatientID.query.filter_by(user_id=user_id).one_or_none()
        if not ds_patient:
            ds_patient = onboard_patient(user_id,0)

        # ADMIN - WORKS
        admin_id = str(current_app.config['DOSESPOT_ADMIN_ID'])
        modobio_clinic_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])

        encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']
        encrypted_user_id = current_app.config['DOSESPOT_ENCRYPTED_ADMIN_ID']
        
        res = get_access_token(modobio_clinic_id, encrypted_clinic_id, admin_id, encrypted_user_id)
        res_json = res.json()
        if res.ok:
            access_token = res_json['access_token']
            headers = {'Authorization': f'Bearer {access_token}'}
        else:
            raise BadRequest(f'DoseSpot returned the following error: {res_json}.')
        
                      
        proxy_ds_user_id = str(current_app.config['DOSESPOT_PROXY_USER_ID'])  
        
        clinic_api_key = current_app.config['DOSESPOT_API_KEY']
        proxy_encrypted_user_id = generate_encrypted_user_id(encrypted_clinic_id[:22], clinic_api_key, proxy_ds_user_id)
        proxy_res = get_access_token(modobio_clinic_id, encrypted_clinic_id, proxy_ds_user_id, proxy_encrypted_user_id)
        proxy_res_json = proxy_res.json()
        if proxy_res.ok:
            proxy_access_token = proxy_res_json['access_token']
            proxy_headers = {'Authorization': f'Bearer {proxy_access_token}'}
        else:
            raise BadRequest(f'DoseSpot returned the following error: {proxy_res_json}.')

        res = requests.get(f'https://my.staging.dosespot.com/webapi/api/patients/{ds_patient.ds_user_id}/pharmacies',headers=proxy_headers)
        res_json = res.json()
        for item in res_json['Items']:
            pharm_id = item['PharmacyId']
            res = requests.delete(f'https://my.staging.dosespot.com/webapi/api/patients/{ds_patient.ds_user_id}/pharmacies/{pharm_id}',headers=proxy_headers)
 
        for item in payload['items']:
            pharm_id = item['pharmacy_id']
            primary_flag = {'SetAsPrimary': item['primary_pharm']}
            res = requests.post(f'https://my.staging.dosespot.com/webapi/api/patients/{ds_patient.ds_user_id}/pharmacies/{pharm_id}',headers=headers,data=primary_flag)
        return
