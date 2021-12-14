import random
import hashlib
import base64
import requests

from flask import current_app
from werkzeug.exceptions import BadRequest
from sqlalchemy import select

from odyssey import db
from odyssey.api.notifications.models import Notifications
from odyssey.utils.constants import ALPHANUMERIC, MODOBIO_ADDRESS
from odyssey.api.dosespot.models import DoseSpotPatientID, DoseSpotPractitionerID
from odyssey.api.dosespot.schemas import (
    DoseSpotCreatePractitionerSchema,
    DoseSpotCreatePatientSchema,
)
from odyssey.api.lookup.models import LookupTerritoriesOfOperations
from odyssey.api.practitioner.models import PractitionerCredentials
from odyssey.api.staff.models import StaffOffices
from odyssey.api.user.models import User


class DoseSpot:
    """Object to handle dose spot routines"""


    
    def __init__(self, practitioner_user_id = None, char_len = 32):
        self.proxy_user_ds_id = current_app.config['DOSESPOT_PROXY_USER_ID']
        self.modobio_clinic_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])
        self.clinic_api_key = current_app.config['DOSESPOT_API_KEY']
        self.encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']
        
        self.rand_phrase = "".join([random.choice(ALPHANUMERIC) for i in range(char_len)])
        
        if practitioner_user_id:
            self.practitioner_ds_id = db.session.execute(select(DoseSpotPractitionerID.ds_user_id).where(DoseSpotPractitionerID.user_id == practitioner_user_id)
                                    ).scalars().one_or_none()
            if not self.practitioner_ds_id:
                raise BadRequest("Practitioner not yet registered with DoseSpot")
        else:
            self.practitioner_ds_id = None

    def registered_practitioners():
        """
        Bring up all practitioners registered with DoseSpot 
        """     
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

    def _generate_encrypted_clinic_id(self):
        """
        This function generates an encrypted clinic key for DoseSpot:
        
        -32 character random alphanumeric phrase
        -append clinic key
        -get the byte value of this string
        -use sha512 to hash the byte value of the combined string
        -get the base64 string out of the hashed string
        -prepend that with the original random phrase

        Reference: 
        
        DoseSpot RESTful API Guide 
        Section 2.3.1 
        """   
        temp_str = self.rand_phrase + self.clinic_api_key

        encoded_str = temp_str.encode('utf-8')

        hash512 = hashlib.sha512(encoded_str).digest()

        encrypted_str = base64.b64encode(hash512).decode()

        while encrypted_str[-1] == '=':
            encrypted_str = encrypted_str[:-1]

        return self.rand_phrase + encrypted_str

    def _generate_encrypted_user_id(self, user_ds_id):
        """
        This function generates an encrypted user_id for DoseSpot
        
        Reference: 
        
        DoseSpot RESTful API Guide 
        Section 2.3.1 

        Params
        ------
        user_ds_id: str
            DoseSpot user id
        """    
        temp_str = str(user_ds_id) + self.encrypted_clinic_id[:22] + self.clinic_api_key
        encoded_str = temp_str.encode('utf-8')

        hash512 = hashlib.sha512(encoded_str).digest()

        encrypted_str = base64.b64encode(hash512).decode()

        while encrypted_str[-1] == '=':
            encrypted_str = encrypted_str[:-1]

        return encrypted_str

    def _generate_sso(self, patient_id=None):
        """
        This is to generate the Single Sign On link for the practitioner.
        WITH patient_id -> SSO will take the practitioner to prescribe to the patient on DS platform
        NO patient_id -> SSO will take the practitioner to DS notifications

        Params
        ------
        patient_id: str
            optional, DoseSpot ID of the patient. 

        Returns
        ------
        sso url
        """
        encrypted_clinic_id_url = self.encrypted_clinic_id.replace('/','%2F')
        encrypted_clinic_id_url = encrypted_clinic_id_url.replace('+','%2B')   

        encrypted_user_id = self._generate_encrypted_user_id(self.practitioner_ds_id)
        encrypted_user_id_url = encrypted_user_id.replace('/','%2F')
        encrypted_user_id_url = encrypted_user_id_url.replace('+','%2B')    
        
        URL = f'http://my.staging.dosespot.com/LoginSingleSignOn.aspx?SingleSignOnClinicId={self.modobio_clinic_id}&SingleSignOnUserId={self.practitioner_ds_id}&SingleSignOnPhraseLength=32&SingleSignOnCode={encrypted_clinic_id_url}&SingleSignOnUserIdVerify={encrypted_user_id_url}'
        
        if(patient_id):
            URL = URL+f'&PatientId={patient_id}'
        else:
            URL = URL+'&RefillsErrors=1'
        return URL

    def _get_access_token(self, user_ds_id):
        """
        Query the DoseSpot API to generate an API access token using the DS user_id and the generated 
        encrypted user_id
        """
        encrypted_user_id = self._generate_encrypted_user_id(user_ds_id)
        payload = {'grant_type': 'password', 'Username':user_ds_id, 'Password':encrypted_user_id}
        
        response = requests.post('https://my.staging.dosespot.com/webapi/token',
                        auth=(self.modobio_clinic_id, self.encrypted_clinic_id),
                        data=payload)
        try:
            response.raise_for_status()
        except:
            raise BadRequest(f'DoseSpot returned the following error: {response.text}')

        return response.json()['access_token']


    def prescribe(self, client_user_id):
        """
        Generates an SSO link for the DoseSpot prescribing portal

        Params
        ------
        patient_id, str: user_id for the client user. Used to bring up the client's dose spot id 

        Returns
        ------
        sso url, str
        """
        client_ds_id = db.session.execute(select(DoseSpotPatientID.ds_user_id).where(DoseSpotPatientID.user_id == client_user_id)
                ).scalars().one_or_none()

        # If the patient does not exist in DoseSpot System yet
        #TODO remove soon. 12.14.21
        if not client_ds_id:
            ds_patient = self.onboard_client(client_user_id)
            client_ds_id = ds_patient.ds_user_id

        return self._generate_sso(client_ds_id)

    def notifications(self):
        """
        Bring up notifications the practitioner has on DoseSpot
        Store these inthe modobio notification system
        """
        # log user in 
        access_token = self._get_access_token(self.practitioner_ds_id)
        headers = {'Authorization': f'Bearer {access_token}'}

        # bring up notifications from dosespot api
        response = requests.get('https://my.staging.dosespot.com/webapi/api/notifications/counts',
                    headers=headers)
        try:
            response.raise_for_status()
        except:
            raise BadRequest(f'DoseSpot returned the following error: {response.text}')

        notification_count = 0
        res_json = response.json()
        for key in res_json:
            if key != 'Result':
                notification_count += res_json[key]

        ds_notification_type = 17 # DoseSpot Notification ID
        url = self._generate_sso()
        # create new or update dosespot notification entry
        # this is done so we do not repeat the same dosespot notification over again, 
        # instead we update the sso url and the notification count
        if notification_count > 0:
            ds_notification = Notifications.query.filter_by(user_id=self.practitioner_ds_id, notification_type_id=ds_notification_type).one_or_none()
            if not ds_notification:
                ds_notification = Notifications(
                    notification_type_id = ds_notification_type, # DoseSpot Notification
                    user_id=self.practitioner_ds_id,
                    title=f"You have {notification_count} DoseSpot Notifications.",
                    content="Click this notification to be brought to the DoseSpot platform to view notifications.",
                    action=url,
                    time_to_live = 0 
                )
                db.session.add(ds_notification)
            else:
                ds_notification.update({'title': f"You have {notification_count} DoseSpot Notifications."})

            db.session.commit()

        return url

    def onboard_client(self, client_user_id : int):
        """
        Create the patient in the DoseSpot System
        """ 
        # PROXY_USER - CAN Create patient on DS platform
    
        access_token = self._get_access_token(self.proxy_user_ds_id)

        headers = {'Authorization': f'Bearer {access_token}'}

        # This user is the patient
        user = User.query.filter_by(user_id = client_user_id).one_or_none()
        
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
        
        payload = {'FirstName': user.firstname,
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
        
        response = requests.post('https://my.staging.dosespot.com/webapi/api/patients',
            headers=headers,
            data=payload)
        
        try:
            response.raise_for_status()
        except:
            raise BadRequest(f'DoseSpot returned the following error: {response.text}')

        res_json = response.json()
        if 'Result' in res_json:
            if 'ResultCode' in res_json['Result']:
                if res_json['Result']['ResultCode'] != 'OK':
                    raise BadRequest(f'DoseSpot returned the following error: {res_json}.')

        ds_patient = DoseSpotCreatePatientSchema().load({'ds_user_id': res_json['Id']})
        ds_patient.user_id = client_user_id
        db.session.add(ds_patient)
        db.session.commit()

        return ds_patient


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