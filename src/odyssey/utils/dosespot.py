import random
import hashlib
import base64
import requests

from flask import current_app
from werkzeug.exceptions import BadRequest
from sqlalchemy import select

from odyssey import db
from odyssey.utils.constants import ALPHANUMERIC, MODOBIO_ADDRESS
from odyssey.api.dosespot.models import DoseSpotPractitionerID
from odyssey.api.dosespot.schemas import (
    DoseSpotCreatePractitionerSchema,
    DoseSpotCreatePatientSchema,
)
from odyssey.api.lookup.models import LookupTerritoriesOfOperations
from odyssey.api.practitioner.models import PractitionerCredentials
from odyssey.api.staff.models import StaffOffices
from odyssey.api.user.models import User

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
    """
    This is to generate the Single Sign On link for the practitioner.
    WITH patient_id -> SSO will take the practitioner to prescribe to the patient on DS platform
    NO patient_id -> SSO will take the practitioner to DS notifications
    """
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

    user = User.query.filter_by(user_id=user_id).one_or_none()
    # reqs: being a staff. office location, verified npi #
    if not user.is_staff:
        raise BadRequest('User must be a practitioner')

    staff_office = StaffOffices.query.filter_by(user_id=user_id).one_or_none()

    if not staff_office:
        raise BadRequest('Staff office not found.')

    credentials = PractitionerCredentials.query.filter_by(user_id=user_id,credential_type='npi').one_or_none()

    if not credentials:
        raise BadRequest('NPI number not found.')
    else:
        if credentials.status == 'Verified':
            npi_number = credentials.credentials
        else:
            raise BadRequest('NPI number has not been verified yet.')

    ds_practitioner = DoseSpotPractitionerID.query.filter_by(user_id=user_id).one_or_none()
    admin_id = str(current_app.config['DOSESPOT_ADMIN_ID'])
    clinic_api_key = current_app.config['DOSESPOT_API_KEY']
    modobio_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])

    # generating keys for ADMIN
    encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']
    encrypted_user_id = current_app.config['DOSESPOT_ENCRYPTED_ADMIN_ID']

    if ds_practitioner:
        raise BadRequest('Practitioner is already in the DoseSpot System.')
    else:
        # Get access token for the Admin
        res = get_access_token(modobio_id,encrypted_clinic_id,admin_id,encrypted_user_id)

        if res.ok:
            access_token = res.json()['access_token']
            headers = {'Authorization': f'Bearer {access_token}'}
        else:
            res_json = res.json()
            raise BadRequest('DoseSpot returned the following error: {res_json}.')
        
        state = LookupTerritoriesOfOperations.query.filter_by(idx=staff_office.territory_id).one_or_none()
        
        # Phone Type
        # 2 - Cell

        # NOTE:
        # If dea and med_lic are empty [], the request works
        # Having trouble sending dea and med_lic to the endpoint
        # HOWEVER, DoseSpot does not require that info, and ModoBio
        # will not be working with controlled substances, so DEA is also unnecessary.
        
        # clin_role_type - 1 = Prescribing Clinician
        # phone_type - 2 = cell
        clin_role_type = 1
        phone_type = 2
        min_payload = {'FirstName': user.firstname,
                'LastName': user.lastname,
                'DateOfBirth': user.dob,
                'Address1': staff_office.street,
                'City':staff_office.city,
                'State':state.sub_territory_abbreviation,
                'ZipCode':staff_office.zipcode,
                'PrimaryPhone': staff_office.phone,
                'PrimaryPhoneType': phone_type,
                'PrimaryFax': staff_office.phone,
                'ClinicianRoleType': clin_role_type,
                'NPINumber': npi_number,
                'DEANumbers': [],
                'MedicalLicenseNumbers': [],
                'Active': True
                }

        res = requests.post(
            'https://my.staging.dosespot.com/webapi/api/clinicians',
            headers=headers,
            data=min_payload)

        # If res is okay, store credentials
        res_json = res.json()
        if res.ok:
            if 'Result' in res_json:
                if 'ResultCode' in res_json['Result']:
                    if res_json['Result']['ResultCode'] != 'OK':
                        raise BadRequest(f'DoseSpot returned the following error: {res_json}.')
            ds_practitioner_id = DoseSpotCreatePractitionerSchema().load(
                                            {'ds_user_id': res_json['Id'],
                                             'ds_enrollment_status': 'pending'
                                            })
            ds_practitioner_id.user_id = user_id
            db.session.add(ds_practitioner_id)
        else:
            raise BadRequest(f'DoseSpot returned the following error: {res_json}.')
    return 201

def onboard_patient(patient_id:int,practitioner_id:int):
    """
    Create the patient in the DoseSpot System
    """ 
    # PROXY_USER - CAN Create patient on DS platform
    # Practitioner_id = 0 means use a Proxy User
    if practitioner_id == 0:
        auth_id = current_app.config['DOSESPOT_PROXY_USER_ID']
    else:
        ds_clinician = DoseSpotPractitionerID.query.filter_by(user_id=practitioner_id).one_or_none()
        auth_id = str(ds_clinician.user_id)
    modobio_clinic_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])
    clinic_api_key = current_app.config['DOSESPOT_API_KEY']
    encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']
    
    encrypted_user_id = generate_encrypted_user_id(encrypted_clinic_id[:22], clinic_api_key, auth_id)    
    res = get_access_token(modobio_clinic_id,encrypted_clinic_id,auth_id,encrypted_user_id)

    res_json = res.json()
    if res.ok:
        access_token = res_json['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
    else:
        raise BadRequest(f'DoseSpot returned the following error: {res_json}.')
    # This user is the patient
    user = User.query.filter_by(user_id=patient_id).one_or_none()
    
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
    phone_type = 2
    min_payload = {'FirstName': user.firstname,
            'LastName': user.lastname,
            'DateOfBirth': user.dob.strftime('%Y-%m-%d'),
            'Gender': gender,
            'Address1': user.client_info.street,
            'City':user.client_info.city,
            'State':state.sub_territory_abbreviation,
            'ZipCode':user.client_info.zipcode,
            'PrimaryPhone': user.phone_number,
            'PrimaryPhoneType': phone_type,
            'Active': True
            }
    
    res = requests.post('https://my.staging.dosespot.com/webapi/api/patients',
        headers=headers,
        data=min_payload)

    res_json = res.json()
    if res.ok:
        if 'Result' in res_json:
            if 'ResultCode' in res_json['Result']:
                if res_json['Result']['ResultCode'] != 'OK':
                    raise BadRequest(f'DoseSpot returned the following error: {res_json}.')
        ds_patient = DoseSpotCreatePatientSchema().load({'ds_user_id': res_json['Id']})
        ds_patient.user_id = patient_id
        db.session.add(ds_patient)
        db.session.commit()
    else:
        # There was an error creating the patient in DoseSpot system
        raise BadRequest(f'DoseSpot returned the following error: {res_json}.')
    return ds_patient

# def onboard_proxy_user():
#     """
#     POST - Only a DoseSpot Admin will be able to use this endpoint. As a workaround
#             we have stored a DoseSpot Admin credentials so the ModoBio system will be able
#             to create the practitioner on the DoseSpot platform
#     """
#     admin_id = str(current_app.config['DOSESPOT_ADMIN_ID'])
#     modobio_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])

#     encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']
#     encrypted_user_id = current_app.config['DOSESPOT_ENCRYPTED_ADMIN_ID']

#     # Get access token for the Admin
#     res = get_access_token(modobio_id,encrypted_clinic_id,admin_id,encrypted_user_id)

#     res_json = res.json()
#     if res.ok:
#         access_token = res_json['access_token']
#         headers = {'Authorization': f'Bearer {access_token}'}
#     else:
#         raise BadRequest(f'DoseSpot returned the following error: {res_json}.')
    
#     # Phone Type
#     # 2 - Cell
#     phone_type = 2
#     # clin_role_type
#     # 1 - Prescribing Practitioner
#     # 6 - Proxy user
#     clin_role_type = 6
#     min_payload = {'FirstName': MODOBIO_ADDRESS['firstname'],
#             'LastName': MODOBIO_ADDRESS['lastname'],
#             'DateOfBirth': MODOBIO_ADDRESS['dob'],
#             'Address1': MODOBIO_ADDRESS['street'],
#             'Address2': MODOBIO_ADDRESS['street2'],
#             'City':MODOBIO_ADDRESS['city'],
#             'State':MODOBIO_ADDRESS['state'],
#             'ZipCode':MODOBIO_ADDRESS['zipcode'],
#             'PrimaryPhone': MODOBIO_ADDRESS['phone'],
#             'PrimaryPhoneType': phone_type,
#             'PrimaryFax': MODOBIO_ADDRESS['phone'],
#             'ClinicianRoleType': clin_role_type,
#             'Active': True
#             }

#     res = requests.post(
#         'https://my.staging.dosespot.com/webapi/api/clinicians',
#         headers=headers,
#         data=min_payload)

#     # If res is okay, store credentials
#     res_json = res.json()
#     if res.ok:
#         if 'Result' in res_json:
#             if 'ResultCode' in res_json['Result']:
#                 if res_json['Result']['ResultCode'] != 'OK':
#                     raise BadRequest(f'DoseSpot returned the following error: {res_json}.')
#         ds_proxy_user = DoseSpotCreateProxyUserSchema().load(
#                                         {'ds_proxy_id': res_json['Id']})
#         db.session.add(ds_proxy_user)
#         db.session.commit()
#     else:
#         raise BadRequest(f'DoseSpot returned the following error: {res_json}.')
#     return ds_proxy_user

def get_access_token(clinic_id,encrypted_clinic_id,clinician_id,encrypted_user_id):
    payload = {'grant_type': 'password','Username':clinician_id,'Password':encrypted_user_id}
    res = requests.post('https://my.staging.dosespot.com/webapi/token',
                    auth=(clinic_id, encrypted_clinic_id),
                    data=payload)
    return res

def lookup_ds_users():
        # Store Modobio info in the response.        
    query = db.session.execute(
        select(User, DoseSpotPractitionerID
        ).join(DoseSpotPractitionerID, DoseSpotPractitionerID.user_id == User.user_id)  
    ).all()

    # create a hashmap lookup table
    lookup_users = {}
    for user,practitioner in query:
        if user not in lookup_users:
            lookup_users[practitioner.ds_user_id] = user    

    return lookup_users