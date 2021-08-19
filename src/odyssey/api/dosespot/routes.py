import os, boto3, secrets, pathlib
import requests

from datetime import datetime
from dateutil.relativedelta import relativedelta

from flask import g, request, current_app
from flask_accepts import accepts, responds
from flask_restx import Resource, Namespace

from odyssey import db

from odyssey.api.user.models import User
from odyssey.api.staff.models import (
    StaffOffices
)
from odyssey.utils.auth import token_auth

from odyssey.utils.errors import (
    UserNotFound, 
    IllegalSetting, 
    ContentNotFound,
    InputError,
    MedicalConditionAlreadySubmitted,
    GenericNotFound,
    UnauthorizedUser
)
from odyssey.utils.misc import check_client_existence, check_blood_test_existence, check_blood_test_result_type_existence, check_medical_condition_existence
from odyssey.utils.dosespot import generate_encrypted_clinic_id, generate_encrypted_user_id, generate_sso, get_access_token
from odyssey.utils.base.resources import BaseResource

ns = Namespace('dosespot', description='Operations related to DoseSpot')

@ns.route('/create-practioner/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class DoseSpotPractitionerCreation(BaseResource):

    @token_auth.login_required
    def get(self, user_id):
        return 

    @token_auth.login_required
    # @accepts(schema=MedicalBloodPressuresSchema, api=ns)
    # @responds(schema=MedicalBloodPressuresSchema, status_code=201, api=ns)
    def post(self, user_id):
        """
        POST - Only a DoseSpot Admin will be able to use this endpoint. As a workaround
               we have stored a DoseSpot Admin credentials so the ModoBio system will be able
               to create the practitioner on the DoseSpot platform
        """

        admin_id = str(current_app.config['DOSESPOT_ADMIN_ID'])
        clinic_api_key = current_app.config['DOSESPOT_API_KEY']
        modobio_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])

        encrypted_clinic_id = generate_encrypted_clinic_id(clinic_api_key)
        encrypted_user_id = generate_encrypted_user_id(encrypted_clinic_id[:22],clinic_api_key,admin_id)


        res = get_access_token(modobio_id,encrypted_clinic_id,admin_id,encrypted_user_id)

        if res.ok:
            access_token = res.json()['access_token']
            headers = {'Authorization': f'Bearer {access_token}'}
        else:
            raise InputError(status_code=405,message=res.json())

        user = User.query.filter_by(user_id=user_id).one_or_none()

        # TODO: check if the user already has a DoseSpot ID
        breakpoint()
        if not user.is_staff:
            raise InputError(status_code=405,message='User must be a practitioner')

        min_payload = {'FirstName': user.firstname,
                'LastName': user.lastname,
                'DateOfBirth': '1995-06-13',
                'Gender': 1,
                'Address1': '123 test ave',
                'City':'Mesa',
                'State':'AZ',
                'ZipCode':'85212',
                'PrimaryPhone': '4803107597',
                'PrimaryPhoneType': 1,
                'PrimaryFax': '4803107597',
                'ClinicianRoleType': 1,
                'NPINumber': '1296336567'
                }

        
        breakpoint()

        # res = requests.post('https://my.staging.dosespot.com/webapi/api/clinicians',
        #         headers=headers,
        #         data=min_payload)
        return 

    @token_auth.login_required(user_type=('client', 'staff'), staff_role=('medical_doctor',), resources=('blood_pressure',))
    @responds(status_code=204, api=ns)
    def delete(self, user_id):
        return