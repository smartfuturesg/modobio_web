from datetime import datetime
import random
import hashlib
import base64
from marshmallow.fields import Dict
import requests
import urllib

from flask import current_app
from werkzeug.exceptions import BadRequest
from sqlalchemy import select

from odyssey import db
from odyssey.api.notifications.models import Notifications
from odyssey.utils.constants import ALPHANUMERIC
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
        self.rand_phrase = "".join([random.choice(ALPHANUMERIC) for i in range(char_len)])
        self.admin_user_ds_id = str(current_app.config['DOSESPOT_ADMIN_ID'])
        self.proxy_user_ds_id = current_app.config['DOSESPOT_PROXY_USER_ID']
        self.modobio_clinic_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])
        self.clinic_api_key = current_app.config['DOSESPOT_API_KEY']
        self.encrypted_clinic_id = self._generate_encrypted_clinic_id(url=False)
        self.encrypted_clinic_id_url = urllib.parse.quote(self.encrypted_clinic_id, safe='')
        self.base_url = current_app.config['DOSESPOT_BASE_URL']

        if practitioner_user_id:
            self.practitioner_ds_id = db.session.execute(select(DoseSpotPractitionerID.ds_user_id).where(DoseSpotPractitionerID.user_id == practitioner_user_id)
                                    ).scalars().one_or_none()
            if not self.practitioner_ds_id:
                raise BadRequest("Practitioner not yet registered with DoseSpot")
        else:
            self.practitioner_ds_id = None

    @staticmethod
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

    def _generate_encrypted_clinic_id(self, url=False):
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

        if url:
            encrypted_str = base64.b64encode(hash512).decode().rstrip('=')
            encrypted_str = urllib.parse.quote(encrypted_str, safe='')
        else:
            encrypted_str = base64.b64encode(hash512).decode().rstrip('=')

        return self.rand_phrase + encrypted_str

    def _generate_encrypted_user_id(self, user_ds_id, url=False):
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

        if url:
            encrypted_str = base64.b64encode(hash512).decode().rstrip('=')
            encrypted_str = urllib.parse.quote(encrypted_str, safe='')
        else:
            encrypted_str = base64.b64encode(hash512).decode().rstrip('=')

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

        encrypted_user_id_url = self._generate_encrypted_user_id(self.practitioner_ds_id, url=True)
        
        params = {
        'SingleSignOnClinicId': self.modobio_clinic_id,
        'SingleSignOnUserId': self.practitioner_ds_id,
        'SingleSignOnPhraseLength': 32,
        'SingleSignOnCode': self.encrypted_clinic_id_url,
        'SingleSignOnUserIdVerify': encrypted_user_id_url
        }

        if(patient_id):
            params['PatientId'] = patient_id
        else:
            params['RefillsErrors'] = 1

        return self.base_url + '/LoginSingleSignOn.aspx?' + urllib.parse.urlencode(params)

    def _get_access_token(self, user_ds_id):
        """
        Query the DoseSpot API to generate an API access token using the DS user_id and the generated 
        encrypted user_id
        """
        encrypted_user_id = self._generate_encrypted_user_id(user_ds_id)
        payload = {'grant_type': 'password', 'Username':user_ds_id, 'Password':encrypted_user_id}

        response = requests.post(self.base_url + '/webapi/token',
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
        client_user_id, str: user_id for the client user. Used to bring up the client's dose spot id 

        Returns
        ------
        sso url, str
        """
        client_ds_id = db.session.execute(select(DoseSpotPatientID.ds_user_id).where(DoseSpotPatientID.user_id == client_user_id)
                ).scalars().one_or_none()

        # If the patient does not exist in DoseSpot System yet, make an account
        #TODO remove soon. 12.14.21
        if not client_ds_id:
            ds_patient = self.onboard_client(client_user_id)
            client_ds_id = ds_patient.ds_user_id

        return self._generate_sso(client_ds_id)

    def notifications(self, user_id):
        """
        Bring up notifications the practitioner has on DoseSpot
        Store these inthe modobio notification system

        Params
        ------
        user_id: int
            modobio user_id
        """
        # log user in 
        access_token = self._get_access_token(self.practitioner_ds_id)
        headers = {'Authorization': f'Bearer {access_token}'}

        # bring up notifications from dosespot api
        response = requests.get(self.base_url + '/webapi/api/notifications/counts',
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
            ds_notification = Notifications.query.filter_by(user_id=user_id, notification_type_id=ds_notification_type).one_or_none()
            if not ds_notification:
                ds_notification = Notifications(
                    notification_type_id = ds_notification_type, # DoseSpot Notification
                    user_id=user_id,
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

        Params
        ------
        client_user_id: int
            Modobio user_id for a client
        """ 
        # This user is the patient
        user = User.query.filter_by(user_id = client_user_id).one_or_none()
        if not user.is_client:
            raise BadRequest("This user is not registered as a client.")
        
        # PROXY_USER - CAN Create patient on DS platform
        access_token = self._get_access_token(self.proxy_user_ds_id)

        headers = {'Authorization': f'Bearer {access_token}'}

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
        
        response = requests.post(self.base_url + '/webapi/api/patients',
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


    def onboard_practitioner(self, staff_user_id):
        """
        Register practitioner with DoseSpot. Pracatitioner must meet the following requirements:
        - valid NPI
        - Staff office 
        - medical_doctor role

        Params
        ------
        staff_user_id: int
            Modobio user_id for a staff member. 
        """
        user = User.query.filter_by(user_id=staff_user_id).one_or_none()
        if not user.is_staff:
            raise BadRequest('User must be a practitioner')

        staff_office = StaffOffices.query.filter_by(user_id=staff_user_id).one_or_none()
        if not staff_office:
            raise BadRequest('Staff office not found.')

        creds = PractitionerCredentials.query.filter_by(user_id=staff_user_id,credential_type='npi', status='Verified').one_or_none()
        if not creds:
            raise BadRequest('Verified NPI number not found for this user.')
        npi_number = creds.credentials
        
        ds_practitioner = DoseSpotPractitionerID.query.filter_by(user_id=staff_user_id).one_or_none()
        if ds_practitioner:
            raise BadRequest('Practitioner is already in the DoseSpot System.')
        
        # Get access token for the Admin account
        access_token = self._get_access_token(self.admin_user_ds_id)

        headers = {'Authorization': f'Bearer {access_token}'}
            
        state = LookupTerritoriesOfOperations.query.filter_by(idx=staff_office.territory_id).one_or_none()

        # NOTE:
        # If dea and med_lic are empty [], the request works
        # Having trouble sending dea and med_lic to the endpoint
        # HOWEVER, DoseSpot does not require that info, and ModoBio
        # will not be working with controlled substances, so DEA is also unnecessary.
        clin_role_type = 1 # prescribing clinician code
        phone_type = 2 # cell phone by default
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

        response = requests.post(
            self.base_url + '/webapi/api/clinicians',
            headers=headers,
            data=min_payload)

        try:
            response.raise_for_status()
        except:
            raise BadRequest(f'DoseSpot returned the following error: {response.text}')

        # If response is okay, store credentials
        res_json = response.json()
        ds_practitioner = DoseSpotCreatePractitionerSchema().load(
                                            {'ds_user_id': res_json['Id'],
                                            'ds_enrollment_status': 'pending'
                                            })
        ds_practitioner.user_id = staff_user_id
        db.session.add(ds_practitioner)
        
        return ds_practitioner

    def allergies(self, client_user_id: int):
        """
        Bring up the allergies to medications using DS API
        """
        ds_patient = DoseSpotPatientID.query.filter_by(user_id=client_user_id).one_or_none()

        if not ds_patient:
            ds_patient = self.onboard_client(client_user_id)
        
        # sign in as proxy user
        access_token = self._get_access_token(self.proxy_user_ds_id)
        headers = {'Authorization': f'Bearer {access_token}'}

        response = requests.get(self.base_url + f'/webapi/api/patients/{ds_patient.ds_user_id}/allergies',
                headers=headers)

        try:
            response.raise_for_status()
        except:
            raise BadRequest(f'DoseSpot returned the following error: {response.text}')
        
        res_json = response.json()
        lookup_users = self.registered_practitioners()

        for item in res_json['Items']:
            if item.get('LastUpdatedUserId') in lookup_users:
                item['modobio_id'] = lookup_users[item['LastUpdatedUserId']].modobio_id
                item['modobio_user_id'] = lookup_users[item['LastUpdatedUserId']].user_id
                item['modobio_name'] = lookup_users[item['LastUpdatedUserId']].firstname + ' ' + lookup_users[item['LastUpdatedUserId']].lastname

            if item.get('OnsetDate'):
                item['OnsetDate'] = datetime.strptime(item['OnsetDate'].split('T')[0], '%Y-%m-%d').date()

        return res_json

    def prescriptions(self, client_user_id: int):
        """
        Query the DoseSpot API for the client's prescriptions
        """
        # Bring up client's ds details. if not registered, make an account
        ds_patient = DoseSpotPatientID.query.filter_by(user_id=client_user_id).one_or_none()

        if not ds_patient:
            ds_patient = self.onboard_client(client_user_id)

        # sign in as proxy user
        access_token = self._get_access_token(self.proxy_user_ds_id)
        headers = {'Authorization': f'Bearer {access_token}'}

        # Some date from a long time ago to today
        start_date = '1970-01-01'
        now = datetime.now()
        end_date = now.strftime("%Y-%m-%d")

        params = {'startDate': start_date, 'endDate': end_date}

        response = requests.get(self.base_url + f'/webapi/api/patients/{ds_patient.ds_user_id}/prescriptions?' + urllib.parse.urlencode(params),
                headers=headers)
        try:
            response.raise_for_status()
        except:
            raise BadRequest(f'DoseSpot returned the following error: {response.text}')
        
        res_json = response.json()

        lookup_users = self.registered_practitioners()

        for item in res_json['Items']:
            if item.get('PrescriberId') in lookup_users:
                item['modobio_id'] = lookup_users[item['PrescriberId']].modobio_id
                item['modobio_user_id'] = lookup_users[item['PrescriberId']].user_id
                item['modobio_name'] = lookup_users[item['PrescriberId']].firstname + ' ' + lookup_users[item['PrescriberId']].lastname

            if item.get('WrittenDate'):
                item['WrittenDate'] = datetime.strptime(item['WrittenDate'].split('T')[0], '%Y-%m-%d').date()

            if item.get('EffectiveDate'):
                item['EffectiveDate'] = datetime.strptime(item['EffectiveDate'].split('T')[0], '%Y-%m-%d').date()

            if item.get('LastFillDate'):
                item['LastFillDate'] = datetime.strptime(item['LastFillDate'].split('T')[0], '%Y-%m-%d').date()

            if item.get('DateInactive'):
                item['DateInactive'] = datetime.strptime(item['DateInactive'].split('T')[0], '%Y-%m-%d').date()

        return res_json

    def enrollment_status(self, user_id, user_type = 'staff'):
        """
        Returns the DoseSpot enrollment status of the user. 
        """
        # Bring up client's ds details. if not registered, make an account
        if user_type == 'client':
            ds_patient = DoseSpotPatientID.query.filter_by(user_id = user_id).one_or_none()
            if ds_patient:
                status = 'enrolled' if ds_patient else 'not enrolled'
        else:
            # check if the practitioner has a dosespot account
            # if they do, check their account status
            #   if the account status is not 'enrolled', query dosespot to see if there are any updates
            ds_practitioner = DoseSpotPractitionerID.query.filter_by(user_id=user_id).one_or_none()
            if not ds_practitioner:
                raise BadRequest('This practitioner does not have a DoseSpot account.')
            
            if ds_practitioner.ds_enrollment_status == 'enrolled':
                status = ds_practitioner.ds_enrollment_status
            else:
                # sign in as admin user
                access_token = self._get_access_token(self.admin_user_ds_id)
                headers = {'Authorization': f'Bearer {access_token}'}
                response = requests.get(self.base_url + f'/webapi/api/clinicians/{ds_practitioner.ds_user_id}',headers=headers)
                try:
                    response.raise_for_status()
                except:
                    raise BadRequest(f'DoseSpot returned the following error: {response.text}')
                res_json = response.json()
                if res_json['Item']!=0:
                    if res_json['Item']['Confirmed'] == True:
                        ds_practitioner.update({'ds_enrollment_status':'enrolled'})
                        db.session.commit()
                        status = 'enrolled'
                    else:
                        status = 'pending'
                else:
                    status = ds_practitioner.ds_enrollment_status

        return status

    def pharmacy_search(self, zipcode = None, state_id = None):
        """
        Returns the pharmacies near the provied address details

        Params
        ------
        zipcode: str
        state_id: int

        Returns
        ------
        parmacies_list: [dict]
            list of pharmacies 
        """
        # Bring up client's ds details. if not registered, make an account
         # Get access token for the Admin account
        access_token = self._get_access_token(self.admin_user_ds_id)

        headers = {'Authorization': f'Bearer {access_token}'}
            
        state = LookupTerritoriesOfOperations.query.filter_by(idx=state_id).one_or_none()

        if zipcode and state:
            params = {'zip': zipcode ,'state' : state.sub_territory_abbreviation}
        elif zipcode:
            params = {'zip': zipcode}
        elif state:
            params = {'state' : state.sub_territory_abbreviation}
        else:
            raise BadRequest('Please select state and/or zipcode for pharmacy search')
       
        response = requests.get(self.base_url + '/webapi/api/pharmacies/search?' + urllib.parse.urlencode(params),headers=headers)

        try:
            response.raise_for_status()
        except:
            raise BadRequest(f'DoseSpot returned the following error: {response.text}')
        
        res_json = response.json()
        
        return res_json

    def client_pharmacies(self, client_user_id: int):
        """
        Bring up the client's pharmacies saved on the DS platform. Use the proxy user for this request
        """
        # Bring up client's ds details. if not registered, make an account
        ds_patient = DoseSpotPatientID.query.filter_by(user_id=client_user_id).one_or_none()

        if not ds_patient:
            ds_patient = self.onboard_client(client_user_id)

        # sign in as proxy user
        access_token = self._get_access_token(self.proxy_user_ds_id)
        headers = {'Authorization': f'Bearer {access_token}'}

        response = requests.get(self.base_url +f'/webapi/api/patients/{ds_patient.ds_user_id}/pharmacies',headers=headers)
       
        try:
            response.raise_for_status()
        except:
            raise BadRequest(f'DoseSpot returned the following error: {response.text}')
        
        res_json = response.json()
        
        return res_json

    def pharmacy_select(self, client_user_id: int, pharmacies: Dict):
        """
        Bring up the client's pharmacies saved on the DS platform. Use the proxy user for this request
        """
        # Bring up client's ds details. if not registered, make an account
        ds_patient = DoseSpotPatientID.query.filter_by(user_id=client_user_id).one_or_none()

        if not ds_patient:
            ds_patient = self.onboard_client(client_user_id)

        # sign in as proxy user
        access_token = self._get_access_token(self.proxy_user_ds_id)
        headers = {'Authorization': f'Bearer {access_token}'}

        #Bring up a list of current pharmacies, remove them from DS
        current_pharmacies = self.client_pharmacies(client_user_id)

        for item in current_pharmacies['Items']:
            pharm_id = item['PharmacyId']
            response = requests.delete(self.base_url + f'/webapi/api/patients/{ds_patient.ds_user_id}/pharmacies/{pharm_id}', headers=headers)
            try:
                response.raise_for_status()
            except:
                raise BadRequest(f'DoseSpot returned the following error: {response.text}')
        
        # log in as admin and submit the new pharmacies
        access_token = self._get_access_token(self.admin_user_ds_id)
        headers = {'Authorization': f'Bearer {access_token}'}
        for item in pharmacies:
            pharm_id = item['pharmacy_id']
            primary_flag = {'SetAsPrimary': item['primary_pharm']}
            response = requests.post(self.base_url + f'/webapi/api/patients/{ds_patient.ds_user_id}/pharmacies/{pharm_id}', headers=headers, data=primary_flag)
            try:
                response.raise_for_status()
            except:
                raise BadRequest(f'DoseSpot returned the following error: {response.text}')

        return


    
