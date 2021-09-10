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
from odyssey.utils.dosespot import generate_sso, get_access_token, onboard_practitioner
from odyssey.utils.base.resources import BaseResource

ns = Namespace('dosespot', description='Operations related to DoseSpot')

@ns.route('/create-practitioner/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class DoseSpotPractitionerCreation(BaseResource):

    @token_auth.login_required
    def get(self, user_id):
        return 

    @token_auth.login_required
    @responds(status_code=201, api=ns)
    def post(self, user_id):
        """
        POST - Only a DoseSpot Admin will be able to use this endpoint. As a workaround
               we have stored a DoseSpot Admin credentials so the ModoBio system will be able
               to create the practitioner on the DoseSpot platform
        """
        return onboard_practitioner(user_id)

    @token_auth.login_required(user_type=('client', 'staff'), staff_role=('medical_doctor',), resources=('blood_pressure',))
    @responds(status_code=204, api=ns)
    def delete(self, user_id):
        return

@ns.route('/prescribe/<int:user_id>/')
class DoseSpotPatientCreation(BaseResource):

    @token_auth.login_required
    def get(self, user_id):
        return 

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

        encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']
        encrypted_user_id = ds_clinician.ds_encrypted_user_id        

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
            else:
                # There was an error creating the patient in DoseSpot system
                raise InputError(status_code=405,message=res.json())

        return {'url': generate_sso(modobio_clinic_id, str(ds_clinician.ds_user_id), encrypted_clinic_id, encrypted_user_id,patient_id=ds_patient_id.ds_user_id)}

    @token_auth.login_required(user_type=('client', 'staff'), staff_role=('medical_doctor',), resources=('blood_pressure',))
    @responds(status_code=204, api=ns)
    def delete(self, user_id):
        return       

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

    @token_auth.login_required(user_type=('staff',),staff_role=('medical_doctor',))
    # @accepts(schema=MedicalBloodPressuresSchema, api=ns)
    # @responds(schema=MedicalBloodPressuresSchema, status_code=201, api=ns)
    def post(self, user_id):
        return

    @token_auth.login_required(user_type=('client', 'staff'), staff_role=('medical_doctor',), resources=('blood_pressure',))
    @responds(status_code=204, api=ns)
    def delete(self, user_id):
        return        
