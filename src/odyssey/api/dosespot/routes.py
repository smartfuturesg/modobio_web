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
    DoseSpotCreatePractitionerSchema,
    DoseSpotCreatePatientSchema,
    DoseSpotPrescribeSSO
)
from odyssey.api.lookup.models import (
    LookupTerritoriesOfOperations,
)

from odyssey.api.user.models import User
from odyssey.utils.auth import token_auth

from odyssey.utils.errors import (
    InputError,
)
from odyssey.utils.dosespot import generate_encrypted_user_id,generate_sso, get_access_token, onboard_practitioner
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
    @responds(schema=DoseSpotPrescribeSSO,status_code=201, api=ns)
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
        ds_patient_id = DoseSpotPatientID.query.filter_by(user_id=user_id).one_or_none()

        modobio_clinic_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])
        clinic_api_key = current_app.config['DOSESPOT_API_KEY']
        encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']
        encrypted_user_id = generate_encrypted_user_id(encrypted_clinic_id[:22],clinic_api_key,str(ds_clinician.ds_user_id))

        # If the patient does not exist in DoseSpot System yet
        if not ds_patient_id:
            # Create the patient in the DoseSpot System

            # Access tokens have expirations, so we will need to generate it each time

            res = get_access_token(modobio_clinic_id,encrypted_clinic_id,str(ds_clinician.ds_user_id),encrypted_user_id)

            if res.ok:
                access_token = res.json()['access_token']
                headers = {'Authorization': f'Bearer {access_token}'}
            else:
                raise InputError(status_code=405,message=res.json())
                
            # Create patient in DoseSpot here
            # Gender
            # 1 - Male
            # 2 - Female
            # 3 - Other
            if user.client_info.gender == 'm':
                gender = 1
            elif user.client_info.gender == 'f':
                gender = 2
            else:
                gender = 3
            state = LookupTerritoriesOfOperations.query.filter_by(idx=user.client_info.territory_id).one_or_none()
            # Phone Type
            # 2 - Cell
            min_payload = {'FirstName': user.firstname,
                    'LastName': user.lastname,
                    'DateOfBirth': user.dob.strftime('%Y-%m-%d'),
                    'Gender': gender,
                    'Address1': user.client_info.street,
                    'City':user.client_info.city,
                    'State':state.sub_territory_abbreviation,
                    'ZipCode':user.client_info.zipcode,
                    'PrimaryPhone': user.phone_number,
                    'PrimaryPhoneType': 2,
                    'Active': True
                    }
            res = requests.post('https://my.staging.dosespot.com/webapi/api/patients',
                headers=headers,
                data=min_payload)

            if res.ok:
                if 'Result' in res.json():
                    if 'ResultCode' in res.json()['Result']:
                        if res.json()['Result']['ResultCode'] != 'OK':
                            raise InputError(status_code=405,message=res.json())                
                ds_patient_id = DoseSpotCreatePatientSchema().load({'ds_user_id': res.json()['Id']})
                ds_patient_id.user_id = user_id
                db.session.add(ds_patient_id)
                db.session.commit()
            else:
                # There was an error creating the patient in DoseSpot system
                raise InputError(status_code=405,message=res.json())

        return {'url': generate_sso(modobio_clinic_id, str(ds_clinician.ds_user_id), encrypted_clinic_id, encrypted_user_id,patient_id=ds_patient_id.ds_user_id)}

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

@ns.route('/pharmacies/')
class DoseSpotPharmacies(BaseResource):

    @token_auth.login_required()
    # @responds(schema=DoseSpotPrescribeSSO,status_code=200, api=ns)
    def get(self):
        """
        GET - Only a ModoBio Practitioners will be able to use this endpoint. This endpoint is used
              to return their enrollment status
        """
        #ADMIN - GET Pharmacies WORKS

        # ds_patient = DoseSpotPatientID.query.filter_by(user_id=user_id).one_or_none()
        # if not ds_patient:
        #     raise InputError(status_code=405,message='This patient does not have a DoseSpot account.')
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

        # TODO Make these inputs
        zipcode = 85255
        state = 'AZ'

        res = requests.get(f'https://my.staging.dosespot.com/webapi/api/pharmacies/search?zip={zipcode}&state={state}',headers=headers)
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


@ns.route('/pharmacies/<int:user_id>/')
class DoseSpotPatientPharmacies(BaseResource):

    @token_auth.login_required()
    # @responds(schema=DoseSpotPrescribeSSO,status_code=200, api=ns)
    def get(self, user_id):
        """
        GET - Only a ModoBio Practitioners will be able to use this endpoint. This endpoint is used
              to return their enrollment status
        """
        
        # ADMIN - Cannot GET, look in to PROXY user
        breakpoint()
        ds_patient = DoseSpotPatientID.query.filter_by(user_id=user_id).one_or_none()
        if not ds_patient:
            raise InputError(status_code=405,message='This patient does not have a DoseSpot account.')
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

        res = requests.get(f'https://my.staging.dosespot.com/webapi/api/patients/{ds_patient.ds_user_id}/pharmacies',headers=headers)
        breakpoint()
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

    @token_auth.login_required()
    @responds(schema=DoseSpotPrescribeSSO,status_code=201, api=ns)
    def post(self, user_id):
        """
        POST - Only a ModoBio Practitioners will be able to use this endpoint. As a workaround
               we have stored a ModoBio Practitioners credentials so the ModoBio system will be able
               to create the practitioner on the DoseSpot platform
        """

        # This user is the patient
        user = User.query.filter_by(user_id=user_id).one_or_none()

        # # DoseSpotPatientID
        ds_patient_id = DoseSpotPatientID.query.filter_by(user_id=user_id).one_or_none()
        
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
        #TODO take this as input
        pharmacy_id = 276

        res = requests.post(f'https://my.staging.dosespot.com/webapi/api/patients/{ds_patient_id.ds_user_id}/pharmacies/{pharmacy_id}',headers=headers)

        return