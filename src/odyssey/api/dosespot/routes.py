import requests
import datetime

from flask import g, request, current_app
from flask_accepts import accepts, responds
from flask.json import dumps
from flask_restx import Resource, Namespace

from odyssey import db

from odyssey.api.dosespot.models import (
    DoseSpotPractitionerID,
    DoseSpotPatientID,
    DoseSpotProxyID
)
from odyssey.api.dosespot.schemas import (
    DoseSpotPrescribeSSO,
    DoseSpotPharmacyNestedSelect,
    DoseSpotEnrollmentGET
)
from odyssey.api.lookup.models import (
    LookupTerritoriesOfOperations,
)

from odyssey.api.notifications.models import Notifications

from odyssey.api.user.models import User
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource
from odyssey.utils.dosespot import (
    generate_encrypted_user_id,
    generate_sso,
    get_access_token,
    onboard_patient,
    onboard_practitioner,
    onboard_proxy_user)

ns = Namespace('dosespot', description='Operations related to DoseSpot')

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
        res = onboard_practitioner(user_id)
        if res == 201:
            db.session.commit()
        return res

@ns.route('/prescribe/<int:user_id>/')
class DoseSpotPatientCreation(BaseResource):
    @token_auth.login_required(user_type=('staff','client'),staff_role=('medical_doctor',))
    @responds(status_code=200, api=ns)
    @ns.doc(params={'start_date': 'prescriptions start range date',
                'end_date':'prescriptions end range date'})
    def get(self, user_id):
        """
        GET - DoseSpot Patient prescribed medications
        """
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date or not end_date:
            raise InputError(status_code=405,message='Must input both start and end dates')
 
        ds_patient = DoseSpotPatientID.query.filter_by(user_id=user_id).one_or_none()
        if not ds_patient:
            ds_patient = onboard_patient(user_id,0)

        clinic_api_key = current_app.config['DOSESPOT_API_KEY']
        modobio_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])

        # generating keys for ADMIN
        encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']

        # PROXY_USER
        # proxy_user = str(232322)
        proxy_user = DoseSpotProxyID.query.one_or_none()
        if not proxy_user:
            proxy_user = onboard_proxy_user()        
        encrypted_user_id = generate_encrypted_user_id(encrypted_clinic_id[:22],clinic_api_key,str(proxy_user.ds_proxy_id))

        res = get_access_token(modobio_id,encrypted_clinic_id,str(proxy_user.ds_proxy_id),encrypted_user_id)
        if res.ok:
            access_token = res.json()['access_token']
            headers = {'Authorization': f'Bearer {access_token}'}
        else:
            raise InputError(status_code=405,message=res.json())

        res = requests.get(f'https://my.staging.dosespot.com/webapi/api/patients/{ds_patient.ds_user_id}/prescriptions?startDate={start_date}&endDate={end_date}',
                headers=headers)

        if not res.ok:
            raise InputError(status_code=405,message=res.json())
        return res.json()['Items']
    @token_auth.login_required(user_type=('staff',),staff_role=('medical_doctor',))      
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

        # DoseSpotPatientID
        ds_patient = DoseSpotPatientID.query.filter_by(user_id=user_id).one_or_none()

        modobio_clinic_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])
        clinic_api_key = current_app.config['DOSESPOT_API_KEY']
        encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']
        encrypted_user_id = generate_encrypted_user_id(encrypted_clinic_id[:22],clinic_api_key,str(ds_clinician.ds_user_id))

        # If the patient does not exist in DoseSpot System yet
        if not ds_patient:
            ds_patient = onboard_patient(user_id,0)

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
        
        curr_user,_ = token_auth.current_user()
        ds_clinician = DoseSpotPractitionerID.query.filter_by(user_id=user_id).one_or_none()
        if not ds_clinician:
            raise InputError(status_code=405,message='This Practitioner does not have a DoseSpot account.')

        modobio_clinic_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])
        clinic_api_key = current_app.config['DOSESPOT_API_KEY']

        encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']
        encrypted_user_id = generate_encrypted_user_id(encrypted_clinic_id[:22],clinic_api_key,str(ds_clinician.ds_user_id))

        res = get_access_token(modobio_clinic_id,encrypted_clinic_id,str(ds_clinician.ds_user_id),encrypted_user_id)
        if res.ok:
            access_token = res.json()['access_token']
            headers = {'Authorization': f'Bearer {access_token}'}
        else:
            raise InputError(status_code=405,message='Could not create')
        
        res = requests.get('https://my.staging.dosespot.com/webapi/api/notifications/counts',headers=headers)
        
        notification_count = 0
        if res.ok:
            for key in res.json():
                if key != 'Result':
                    notification_count+=res.json()[key]
        else:
            raise InputError(status_code=405,message=res.json())

        url = generate_sso(modobio_clinic_id, str(ds_clinician.ds_user_id), encrypted_clinic_id, encrypted_user_id)
        
        ds_notification_type = 17 # DoseSpot Notification ID
        ds_notification = Notifications.query.filter_by(user_id=user_id,notification_type_id=ds_notification_type).one_or_none()
        if not ds_notification:
            ds_notification = Notifications(
                notification_type_id=ds_notification_type, # DoseSpot Notification
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

        return {'url': url}

@ns.route('/enrollment-status/<int:user_id>/')
class DoseSpotNotificationSSO(BaseResource):
    @token_auth.login_required(user_type=('staff',),staff_role=('medical_doctor',))
    @responds(schema=DoseSpotEnrollmentGET,status_code=200, api=ns)
    def get(self, user_id):
        """
        GET - Only a ModoBio Practitioners will be able to use this endpoint. This endpoint is used
              to return their enrollment status
        """

        ds_practitioner = DoseSpotPractitionerID.query.filter_by(user_id=user_id).one_or_none()
        if not ds_practitioner:
            raise InputError(status_code=405,message='This Practitioner does not have a DoseSpot account.')
        
        if ds_practitioner.ds_enrollment_status == 'enrolled':
            return {'status': ds_practitioner.ds_enrollment_status}

        admin_id = str(current_app.config['DOSESPOT_ADMIN_ID'])
        clinic_api_key = current_app.config['DOSESPOT_API_KEY']
        modobio_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])

        # generating keys for ADMIN
        encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']
        encrypted_user_id = generate_encrypted_user_id(encrypted_clinic_id[:22],clinic_api_key,admin_id)    

        res = get_access_token(modobio_id,encrypted_clinic_id,admin_id,encrypted_user_id)
        if res.ok:
            access_token = res.json()['access_token']
            headers = {'Authorization': f'Bearer {access_token}'}
        else:
            raise InputError(status_code=405,message='Could not create')

        res = requests.get(f'https://my.staging.dosespot.com/webapi/api/clinicians/{ds_practitioner.ds_user_id}',headers=headers)
        if res.ok:
            # Confirmed = True means DoseSpot has verified the NPI number            
            if res.json()['Item']!=0:
                if res.json()['Item']['Confirmed'] == True:
                    ds_practitioner.update({'ds_enrollment_status':'enrolled'})
                    db.session.commit()
                    ds_practitioner.ds_enrollment_status = 'enrolled'
        return {'status': ds_practitioner.ds_enrollment_status}

@ns.route('/select/pharmacies/<int:user_id>/')
class DoseSpotSelectPharmacies(BaseResource):
    @token_auth.login_required(user_type=('client',))
    def get(self,user_id):
        """
        GET - This is to display to the Modobio client the pharmacies available to them
              given their state and zipcode

            DoseSpot Admin credentials will be used for this endpoint
        """
        admin_id = str(current_app.config['DOSESPOT_ADMIN_ID'])
        modobio_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])
        clinic_api_key = current_app.config['DOSESPOT_API_KEY']

        encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']
        encrypted_user_id = generate_encrypted_user_id(encrypted_clinic_id[:22],clinic_api_key,admin_id)    

        res = get_access_token(modobio_id,encrypted_clinic_id,admin_id,encrypted_user_id)
        if res.ok:
            access_token = res.json()['access_token']
            headers = {'Authorization': f'Bearer {access_token}'}
        else:
            raise InputError(status_code=403,message=res.json())

        user = User.query.filter_by(user_id=user_id).one_or_none()
        state = LookupTerritoriesOfOperations.query.filter_by(idx=user.client_info.territory_id).one_or_none()

        res = requests.get(f'https://my.staging.dosespot.com/webapi/api/pharmacies/search?zip={user.client_info.zipcode}&state={state.sub_territory_abbreviation}',headers=headers)
        if not res.ok:
            raise InputError(status_code=405,message=res.json())
        return res.json()['Items']

@ns.route('/pharmacies/<int:user_id>/')
class DoseSpotPatientPharmacies(BaseResource):
    @token_auth.login_required(user_type=('client',))
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

        proxy_user = DoseSpotProxyID.query.one_or_none()
        if not proxy_user:
            proxy_user = onboard_proxy_user()
        
        encrypted_user_id = generate_encrypted_user_id(encrypted_clinic_id[:22],clinic_api_key,str(proxy_user.ds_proxy_id))

        res = get_access_token(modobio_id,encrypted_clinic_id,str(proxy_user.ds_proxy_id),encrypted_user_id)
        if res.ok:
            access_token = res.json()['access_token']
            headers = {'Authorization': f'Bearer {access_token}'}
        else:
            raise InputError(status_code=405,message=res.json())

        res = requests.get(f'https://my.staging.dosespot.com/webapi/api/patients/{ds_patient.ds_user_id}/pharmacies',headers=headers)
        
        if not res.ok:
            raise InputError(status_code=405,message=res.json())
        return res.json()['Items']

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
            raise InputError(status_code=405,message='Can only select up to 3 pharmacies.')

        primary_pharm_count = 0
        for item in payload['items']:
            if item['primary_pharm']:
                primary_pharm_count+=1
            if primary_pharm_count > 1:
                raise InputError(status_code=405,message='Must select only 1 pharmacy to be set as primary')
        if primary_pharm_count == 0:
            raise InputError(status_code=405,message='Must select 1 pharmacy to be set as primary')

        # # DoseSpotPatientID
        ds_patient = DoseSpotPatientID.query.filter_by(user_id=user_id).one_or_none()
        if not ds_patient:
            ds_patient = onboard_patient(user_id,0)

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
        
        proxy_user = DoseSpotProxyID.query.one_or_none()
        if not proxy_user:
            proxy_user = onboard_proxy_user()        
        
        clinic_api_key = current_app.config['DOSESPOT_API_KEY']
        proxy_encrypted_user_id = generate_encrypted_user_id(encrypted_clinic_id[:22],clinic_api_key,str(proxy_user.ds_proxy_id))
        proxy_res = get_access_token(modobio_clinic_id,encrypted_clinic_id,str(proxy_user.ds_proxy_id),proxy_encrypted_user_id)
        if proxy_res.ok:
            proxy_access_token = proxy_res.json()['access_token']
            proxy_headers = {'Authorization': f'Bearer {proxy_access_token}'}
        else:
            raise InputError(status_code=405,message=res.json())

        res = requests.get(f'https://my.staging.dosespot.com/webapi/api/patients/{ds_patient.ds_user_id}/pharmacies',headers=proxy_headers)

        for item in res.json()['Items']:
            pharm_id = item['PharmacyId']
            res = requests.delete(f'https://my.staging.dosespot.com/webapi/api/patients/{ds_patient.ds_user_id}/pharmacies/{pharm_id}',headers=proxy_headers)
 
        for item in payload['items']:
            pharm_id = item['pharmacy_id']
            primary_flag = {'SetAsPrimary': item['primary_pharm']}
            res = requests.post(f'https://my.staging.dosespot.com/webapi/api/patients/{ds_patient.ds_user_id}/pharmacies/{pharm_id}',headers=headers,data=primary_flag)
        return