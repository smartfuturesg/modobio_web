import random
import hashlib
import base64
import requests
import os, boto3, secrets, pathlib, json
import requests

from datetime import datetime
from dateutil.relativedelta import relativedelta

from flask import g, request, current_app
from flask_accepts import accepts, responds
from flask.json import dumps
from flask_restx import Resource, Namespace
from odyssey import db

from odyssey.utils.constants import ALPHANUMERIC

from odyssey.api.dosespot.models import (
    DoseSpotPractitionerID,
    DoseSpotPatientID
)
from odyssey.api.dosespot.schemas import (
    DoseSpotCreatePractitionerSchema,
    DoseSpotCreatePatientSchema
)
from odyssey.api.lookup.models import (
    LookupTerritoriesOfOperations,
)
from odyssey.api.practitioner.models import PractitionerCredentials
from odyssey.api.staff.models import (
    StaffOffices
)
from odyssey.api.user.models import User
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

def generate_encrypted_clinic_id(clinic_key,char_len=32):
    """
    This function generates an encrypted clinic key for DoseSpot
    
    Reference: 
    
    DoseSpot RESTful API Guide 
    Section 2.3.1 
    """
    rand_phrase = "".join([random.choice(ALPHANUMERIC) for i in range(char_len)])

    temp_str = rand_phrase + clinic_key

    encoded_str = temp_str.encode('utf-8')

    hash512 = hashlib.sha512(encoded_str).digest()

    encrypted_str = base64.b64encode(hash512).decode()

    while encrypted_str[-1] == '=':
        encrypted_str = encrypted_str[:-1]

    return rand_phrase+encrypted_str

def generate_encrypted_user_id(rand_phrase,clinic_key,clinician_id):
    """
    This function generates an encrypted user_id for DoseSpot
    
    Reference: 
    
    DoseSpot RESTful API Guide 
    Section 2.3.1 
    """    
    temp_str = clinician_id + rand_phrase + clinic_key
    encoded_str = temp_str.encode('utf-8')

    hash512 = hashlib.sha512(encoded_str).digest()

    encrypted_str = base64.b64encode(hash512).decode()

    while encrypted_str[-1] == '=':
        encrypted_str = encrypted_str[:-1]

    return encrypted_str

def generate_sso(clinic_id, clinician_id, encrypted_clinic_id, encrypted_user_id, patient_id=None):
    # This is to generate the Single Sign On link for the practitioner.
    # WITH patient_id -> SSO will take the practitioner to prescribe to the patient on DS platform
    # NO patient_id -> SSO will take the practitioner to DS notifications
    encrypted_clinic_id_url = encrypted_clinic_id.replace('/','%2F')
    encrypted_clinic_id_url = encrypted_clinic_id_url.replace('+','%2B')            
    encrypted_user_id_url = encrypted_user_id.replace('/','%2F')
    encrypted_user_id_url = encrypted_user_id_url.replace('+','%2B')    
    URL = f'http://my.staging.dosespot.com/LoginSingleSignOn.aspx?SingleSignOnClinicId={clinic_id}&SingleSignOnUserId={clinician_id}&SingleSignOnPhraseLength=32&SingleSignOnCode={encrypted_clinic_id_url}&SingleSignOnUserIdVerify={encrypted_user_id_url}'
    if(patient_id):
        URL = URL+f'&PatientId={patient_id}'
    else:
        URL = URL+'&RefillsErrors=1'
    return URL

def onboard_practitioner(user_id):
    """
    POST - Only a DoseSpot Admin will be able to use this endpoint. As a workaround
            we have stored a DoseSpot Admin credentials so the ModoBio system will be able
            to create the practitioner on the DoseSpot platform
    """
    ds_practitioner = DoseSpotPractitionerID.query.filter_by(user_id=user_id).one_or_none()
    admin_id = str(current_app.config['DOSESPOT_ADMIN_ID'])
    clinic_api_key = current_app.config['DOSESPOT_API_KEY']
    modobio_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])

    # generating keys for ADMIN
    encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']
    encrypted_user_id = current_app.config['DOSESPOT_ENCRYPTED_ADMIN_ID']

    if ds_practitioner:
        raise InputError(status_code=405,message='Practitioner is already in the DoseSpot System.')
    else:
        # Get access token for the Admin
        res = get_access_token(modobio_id,encrypted_clinic_id,admin_id,encrypted_user_id)

        if res.ok:
            access_token = res.json()['access_token']
            headers = {'Authorization': f'Bearer {access_token}'}
        else:
            raise InputError(status_code=405,message=res.json())

        user = User.query.filter_by(user_id=user_id).one_or_none()

        if not user.is_staff:
            raise InputError(status_code=405,message='User must be a practitioner')
        
        missing_inputs = []


        staff_office = StaffOffices.query.filter_by(user_id=user_id).one_or_none()

        if not staff_office:
            missing_inputs.append(1)

        credentials = PractitionerCredentials.query.filter_by(user_id=user_id,credential_type='npi').one_or_none()

        npi_number = ''
        if not credentials:
            missing_inputs.append(2)
        else:              
            if credentials.status == 'Verified':
                npi_number = credentials.credentials
            else:
                raise InputError(status_code=405,message='NPI number has not been verified yet.')


        if not npi_number:
            missing_inputs.append(2)                        
        
        if missing_inputs:
            if [1,2] in missing_inputs:
                raise InputError(status_code=405,message='Missing both Office Information and Practitioner Credentials')
            elif 1 in missing_inputs:
                raise InputError(status_code=406,message='Missing Office Information')
            else:
                raise InputError(status_code=407,message='Missing Practitioner Credentials, Needs at least NPI number.')

        state = LookupTerritoriesOfOperations.query.filter_by(idx=staff_office.territory_id).one_or_none()
        
        
        # Phone Type
        # 2 - Cell

        # NOTE:
        # If dea and med_lic are empty [], the request works
        # Having trouble sending dea and med_lic to the endpoint
        # HOWEVER, DoseSpot does not require that info, and ModoBio
        # will not be working with controlled substances, so DEA is also unnecessary.

        min_payload = {'FirstName': user.firstname,
                'LastName': user.lastname,
                'DateOfBirth': user.dob,
                'Address1': staff_office.street,
                'City':staff_office.city,
                'State':state.sub_territory_abbreviation,
                'ZipCode':staff_office.zipcode,
                'PrimaryPhone': staff_office.phone,
                'PrimaryPhoneType': 2,
                'PrimaryFax': staff_office.phone,
                'ClinicianRoleType': 1,
                'NPINumber': npi_number,
                'DEANumbers': [],
                'MedicalLicenseNumbers': [],
                'Active': True
                }
                
        res = requests.post('https://my.staging.dosespot.com/webapi/api/clinicians',headers=headers,data=min_payload)

        # If res is okay, store credentials
        if res.ok:
            if 'Result' in res.json():
                if 'ResultCode' in res.json()['Result']:
                    if res.json()['Result']['ResultCode'] != 'OK':
                        raise InputError(status_code=405,message=res.json())
            ds_encrypted_user_id = generate_encrypted_user_id(encrypted_clinic_id[:22],clinic_api_key,str(res.json()['Id']))
            ds_practitioner_id = DoseSpotCreatePractitionerSchema().load(
                                            {'ds_encrypted_user_id': ds_encrypted_user_id,
                                                'ds_user_id': res.json()['Id'],
                                                'ds_enrollment_status': 'pending'
                                                })
            ds_practitioner_id.user_id = user_id
            db.session.add(ds_practitioner_id)
        else:
            raise InputError(status_code=405,message=res.json())
    return

def get_access_token(clinic_id,encrypted_clinic_id,clinician_id,encrypted_user_id):
    payload = {'grant_type': 'password','Username':clinician_id,'Password':encrypted_user_id}
    res = requests.post('https://my.staging.dosespot.com/webapi/token',
                    auth=(clinic_id, encrypted_clinic_id),
                    data=payload)
    return res

