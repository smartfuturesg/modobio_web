import os, boto3, secrets, pathlib, json
import requests

from datetime import datetime
from dateutil.relativedelta import relativedelta

from flask import g, request, current_app
from flask_accepts import accepts, responds
from flask.json import dumps
from flask_restx import Resource, Namespace

from odyssey import db

from odyssey.api.dosespot.models import (
    DoseSpotPractitionerID,
    DoseSpotPatientID
)
from odyssey.api.dosespot.schemas import (
    DoseSpotPrescribeSSO,
    DoseSpotPharmacyNestedSelect
)
from odyssey.api.lookup.models import (
    LookupTerritoriesOfOperations,
)

from odyssey.api.user.models import User
from odyssey.utils.auth import token_auth

from odyssey.utils.errors import (
    InputError,
)
from odyssey.utils.dosespot import generate_encrypted_user_id,generate_sso, get_access_token, onboard_practitioner, onboard_patient
from odyssey.utils.base.resources import BaseResource

ns = Namespace('dosespot', description='Operations related to DoseSpot')

@ns.route('/create-practitioner/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class DoseSpotPractitionerCreation(BaseResource):
    @token_auth.login_required(user_type=('staff',),staff_role=('medical_doctor',))
    @responds(status_code=201, api=ns)
    def post(self, user_id):
        """
        POST - Only a DoseSpot Admin will be able to use this endpoint. As a workaround
               we have stored a DoseSpot Admin credentials so the ModoBio system will be able
               to create the practitioner on the DoseSpot platform
        """
        return onboard_practitioner(user_id)

@ns.route('/prescribe/<int:user_id>/')
class DoseSpotPatientCreation(BaseResource):
    @token_auth.login_required(user_type=('staff',),staff_role=('medical_doctor',))
    @responds(schema=DoseSpotPrescribeSSO,status_code=200, api=ns)
    def get(self, user_id):
        """
        GET - DoseSpot Patient prescribed medications
        """
        ds_patient = DoseSpotPatientID.query.filter_by(user_id=user_id).one_or_none()
        if not ds_patient:
            raise InputError(status_code=405,message='This patient does not have a DoseSpot account.')
        clinic_api_key = current_app.config['DOSESPOT_API_KEY']
        modobio_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])

        # generating keys for ADMIN
        encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']
        encrypted_user_id = current_app.config['DOSESPOT_ENCRYPTED_ADMIN_ID']

        # PROXY_USER
        proxy_user = str(232322)
        encrypted_user_id = generate_encrypted_user_id(encrypted_clinic_id[:22],clinic_api_key,proxy_user)

        res = get_access_token(modobio_id,encrypted_clinic_id,proxy_user,encrypted_user_id)
        if res.ok:
            access_token = res.json()['access_token']
            headers = {'Authorization': f'Bearer {access_token}'}
        else:
            raise InputError(status_code=405,message=res.json())

        res = requests.get(f'https://my.staging.dosespot.com/webapi/api/patients/{ds_patient.ds_user_id}/pharmacies',headers=headers)
        """
        Section 4.2.10 Registration type in DoseSpot RESTful API Guide
        Return Items:
        1 - Pending
        3 - Remove

        Confirmed = True means DoseSpot has verified the NPI number
        """
        if res.json()['Item']!=0:
            if res.json()['Item']['Confirmed'] == True:
                pass
        return         
    @responds(schema=DoseSpotPrescribeSSO,status_code=201,api=ns)
    def post(self, user_id):
        """
        POST - Only a ModoBio Practitioners will be able to use this endpoint. As a workaround
               we have stored a ModoBio Practitioners credentials so the ModoBio system will be able
               to create the practitioner on the DoseSpot platform
        """

        # Clinician ID 
        curr_user,_ = token_auth.current_user()
        ds_clinician = DoseSpotPractitionerID.query.filter_by(user_id=curr_user.user_id).one_or_none()
        if not ds_clinician:
            raise InputError(status_code=405,message='This Practitioner does not have a DoseSpot account.')

        # This user is the patient
        user = User.query.filter_by(user_id=user_id).one_or_none()

        # DoseSpotPatientID
        ds_patient = DoseSpotPatientID.query.filter_by(user_id=user_id).one_or_none()

        modobio_clinic_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])
        clinic_api_key = current_app.config['DOSESPOT_API_KEY']
        encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']
        encrypted_user_id = generate_encrypted_user_id(encrypted_clinic_id[:22],clinic_api_key,str(ds_clinician.ds_user_id))

        # If the patient does not exist in DoseSpot System yet
        if not ds_patient:
            ds_patient = onboard_patient(user_id,curr_user.user_id)

        return {'url': generate_sso(modobio_clinic_id, str(ds_clinician.ds_user_id), encrypted_clinic_id, encrypted_user_id,patient_id=ds_patient.ds_user_id)}

@ns.route('/notifications/<int:user_id>/')
class DoseSpotNotificationSSO(BaseResource):
    @token_auth.login_required(user_type=('staff',),staff_role=('medical_doctor',))
    @responds(schema=DoseSpotPrescribeSSO,status_code=200, api=ns)
    def get(self, user_id):
        """
        GET - Only a ModoBio Practitioners will be able to use this endpoint. This endpoint is used
              to return the SSO Link 
        """

        # Clinician ID 
        curr_suer,_ = token_auth.current_user()
        ds_clinician = DoseSpotPractitionerID.query.filter_by(user_id=user_id).one_or_none()
        if not ds_clinician:
            raise InputError(status_code=405,message='This Practitioner does not have a DoseSpot account.')

        modobio_clinic_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])

        encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']
        encrypted_user_id = str(ds_clinician.ds_encrypted_user_id)

        return {'url': generate_sso(modobio_clinic_id, str(ds_clinician.ds_user_id), encrypted_clinic_id, encrypted_user_id)}

@ns.route('/enrollment-status/<int:user_id>/')
class DoseSpotNotificationSSO(BaseResource):

    @token_auth.login_required(user_type=('staff',),staff_role=('medical_doctor',))
    @responds(schema=DoseSpotPrescribeSSO,status_code=200, api=ns)
    def get(self, user_id):
        """
        GET - Only a ModoBio Practitioners will be able to use this endpoint. This endpoint is used
              to return their enrollment status
        """

        ds_practitioner = DoseSpotPractitionerID.query.filter_by(user_id=user_id).one_or_none()
        if not ds_practitioner:
            raise InputError(status_code=405,message='This Practitioner does not have a DoseSpot account.')
        admin_id = str(current_app.config['DOSESPOT_ADMIN_ID'])
        clinic_api_key = current_app.config['DOSESPOT_API_KEY']
        modobio_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])

        # generating keys for ADMIN
        encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']
        encrypted_user_id = current_app.config['DOSESPOT_ENCRYPTED_ADMIN_ID']
        res = get_access_token(modobio_id,encrypted_clinic_id,admin_id,encrypted_user_id)
        if res.ok:
            access_token = res.json()['access_token']
            headers = {'Authorization': f'Bearer {access_token}'}
        else:
            raise InputError(status_code=405,message=res.json())

        res = requests.get(f'https://my.staging.dosespot.com/webapi/api/clinicians/{ds_practitioner.ds_user_id}',headers=headers)
        if res.ok:
            # Confirmed = True means DoseSpot has verified the NPI number            
            if res.json()['Item']!=0:
                if res.json()['Item']['Confirmed'] == True:
                    ds_practitioner.update({'ds_enrollment_status':'enrolled'})
                    db.session.commit()
                    ds_practitioner.ds_enrollment_status = 'enrolled'
        return {'enrollment_status': ds_practitioner.ds_enrollment_status}

@ns.route('/select/pharmacies/<int:user_id>/')
class DoseSpotSelectPharmacies(BaseResource):
    @token_auth.login_required()
    def get(self,user_id):
        """
        GET - This is to display to the Modobio client the pharmacies available to them
              given their state and zipcode

            DoseSpot Admin credentials will be used for this endpoint
        """
        admin_id = str(current_app.config['DOSESPOT_ADMIN_ID'])
        modobio_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])

        encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']
        encrypted_user_id = current_app.config['DOSESPOT_ENCRYPTED_ADMIN_ID']
        res = get_access_token(modobio_id,encrypted_clinic_id,admin_id,encrypted_user_id)
        if res.ok:
            access_token = res.json()['access_token']
            headers = {'Authorization': f'Bearer {access_token}'}
        else:
            raise InputError(status_code=405,message=res.json())

        user = User.query.filter_by(user_id=user_id).one_or_none()
        state = LookupTerritoriesOfOperations.query.filter_by(idx=user.client_info.territory_id).one_or_none()

        res = requests.get(f'https://my.staging.dosespot.com/webapi/api/pharmacies/search?zip={user.client_info.zipcode}&state={state.sub_territory_abbreviation}',headers=headers)
        if not res.ok:
            raise InputError(status_code=405,message=res.json())
        return res.json()['Items']

@ns.route('/pharmacies/<int:user_id>/')
class DoseSpotPatientPharmacies(BaseResource):
    @token_auth.login_required()
    # @responds(schema=DoseSpotPrescribeSSO,status_code=200, api=ns)
    def get(self, user_id):
        """
        GET - The pharmacies the Modobio client has selected (at most 3.)

            DoseSpot Proxy credentials will be used to access DoseSpot credentials
        """
        
        # ADMIN - Cannot GET, look in to PROXY user
        # PROXY user WORKS
        ds_patient = DoseSpotPatientID.query.filter_by(user_id=user_id).one_or_none()

        if not ds_patient:
            # This works
            ds_patient = onboard_patient(user_id,0)

        clinic_api_key = current_app.config['DOSESPOT_API_KEY']
        modobio_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])

        # generating keys for ADMIN
        encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']
        encrypted_user_id = current_app.config['DOSESPOT_ENCRYPTED_ADMIN_ID']

        # TODO: store PROXY_USER
        proxy_user = str(232322)
        encrypted_user_id = generate_encrypted_user_id(encrypted_clinic_id[:22],clinic_api_key,proxy_user)

        res = get_access_token(modobio_id,encrypted_clinic_id,proxy_user,encrypted_user_id)
        if res.ok:
            access_token = res.json()['access_token']
            headers = {'Authorization': f'Bearer {access_token}'}
        else:
            raise InputError(status_code=405,message=res.json())

        res = requests.get(f'https://my.staging.dosespot.com/webapi/api/patients/{ds_patient.ds_user_id}/pharmacies',headers=headers)
        
        if not res.ok:
            raise InputError(status_code=405,message=res.json())
        return res.json()['Items']

    @token_auth.login_required()
    @accepts(schema=DoseSpotPharmacyNestedSelect)
    def post(self, user_id):
        """
        POST - The pharmacies the Modobio client has selected (at most 3.)
   
               DoseSpot Admin credentials will be used for this endpoint
        """
        payload = request.json
        if len(payload['items'])>3:
            raise InputError(status_code=405,message='Can only select up to 3 pharmacies.')
        # This user is the patient
        user = User.query.filter_by(user_id=user_id).one_or_none()

        # # DoseSpotPatientID
        ds_patient = DoseSpotPatientID.query.filter_by(user_id=user_id).one_or_none()
        
        # ADMIN - WORKS
        admin_id = str(current_app.config['DOSESPOT_ADMIN_ID'])
        modobio_clinic_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])

        encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']
        encrypted_user_id = current_app.config['DOSESPOT_ENCRYPTED_ADMIN_ID']
        res = get_access_token(modobio_clinic_id,encrypted_clinic_id,admin_id,encrypted_user_id)

        if res.ok:
            access_token = res.json()['access_token']
            headers = {'Authorization': f'Bearer {access_token}'}
        else:
            raise InputError(status_code=405,message=res.json())
        
        # Get the client's pharmacies to delete
        res = requests.get(f'https://my.staging.dosespot.com/webapi/api/patients/{ds_patient.ds_user_id}/pharmacies',headers=headers)

        for item in res.json()['Items']:
            pharm_id = item['PharmacyId']
            res = requests.delete(f'https://my.staging.dosespot.com/webapi/api/patients/{ds_patient.ds_user_id}/pharmacies/{pharm_id}',headers=headers)
 

        for pharm_id in payload['items']:
            res = requests.post(f'https://my.staging.dosespot.com/webapi/api/patients/{ds_patient.ds_user_id}/pharmacies/{pharm_id}',headers=headers)
        
        return