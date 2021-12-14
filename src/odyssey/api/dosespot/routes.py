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
    generate_sso,
    get_access_token,
    lookup_ds_users,
    onboard_patient,
    onboard_practitioner
)

ns = Namespace('dosespot', description='Operations related to DoseSpot')

@ns.route('/allergies/<int:user_id>/')
class DoseSpotAllergies(BaseResource):
    @token_auth.login_required(user_type=('staff','client'),staff_role=('medical_doctor',))
    @responds(schema=DoseSpotAllergyOutput,status_code=200,api=ns)
    def get(self, user_id):
        """
        GET - DoseSpot Patient prescribed medications
        """
        ds_patient = DoseSpotPatientID.query.filter_by(user_id=user_id).one_or_none()
        if not ds_patient:
            ds_patient = onboard_patient(user_id,0)

        clinic_api_key = current_app.config['DOSESPOT_API_KEY']
        modobio_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])

        # generating keys for ADMIN
        encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']

        # PROXY_USER
        proxy_ds_user_id = str(current_app.config['DOSESPOT_PROXY_USER_ID'])  
        encrypted_user_id = generate_encrypted_user_id(encrypted_clinic_id[:22], clinic_api_key, proxy_ds_user_id)

        res = get_access_token(modobio_id,encrypted_clinic_id, proxy_ds_user_id, encrypted_user_id)
        res_json = res.json()
        if res.ok:
            access_token = res_json['access_token']
            headers = {'Authorization': f'Bearer {access_token}'}
        else:
            raise BadRequest(f'DoseSpot returned the following error: {res_json}.')

        res = requests.get(f'https://my.staging.dosespot.com/webapi/api/patients/{ds_patient.ds_user_id}/allergies',
                headers=headers)
        res_json = res.json()

        if not res.ok:
            raise BadRequest(f'DoseSpot returned the following error: {res_json}.')
        
        if 'Items' not in res_json:
            raise BadRequest(f'DoseSpot may have changed their API output, please reach out to a staff admin.')
        
        lookup_users = lookup_ds_users()

        for item in res_json['Items']:
            if item.get('LastUpdatedUserId') in lookup_users:
                item['modobio_id'] = lookup_users[item['LastUpdatedUserId']].modobio_id
                item['modobio_user_id'] = lookup_users[item['LastUpdatedUserId']].user_id
                item['modobio_name'] = lookup_users[item['LastUpdatedUserId']].firstname + ' ' + lookup_users[item['LastUpdatedUserId']].lastname

            if item.get('OnsetDate'):
                item['OnsetDate'] = datetime.strptime(item['OnsetDate'].split('T')[0], '%Y-%m-%d').date()

        payload = {'items': res_json['Items'],
                   'total_items': len(res_json['Items'])}

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
        res = onboard_practitioner(user_id)
        if res == 201:
            db.session.commit()
        return res

@ns.route('/prescribe/<int:user_id>/')
class DoseSpotPatientCreation(BaseResource):
    @token_auth.login_required(user_type=('staff','client'),staff_role=('medical_doctor',))
    @responds(schema=DoseSpotPrescribedOutput,status_code=200,api=ns)
    def get(self, user_id):
        """
        GET - DoseSpot Patient prescribed medications
        """
        # Some date from a long time ago to today
        start_date = '1970-01-01'
        now = datetime.now()
        end_date = now.strftime("%Y-%m-%d")

        if not start_date or not end_date:
            raise BadRequest('Please provide both start and end dates.')
 
        ds_patient = DoseSpotPatientID.query.filter_by(user_id=user_id).one_or_none()
        if not ds_patient:
            ds_patient = onboard_patient(user_id,0)

        clinic_api_key = current_app.config['DOSESPOT_API_KEY']
        modobio_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])

        # generating keys for ADMIN
        encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']

        # PROXY_USER
        proxy_ds_user_id = str(current_app.config['DOSESPOT_PROXY_USER_ID'])         
        encrypted_user_id = generate_encrypted_user_id(encrypted_clinic_id[:22],clinic_api_key, proxy_ds_user_id)

        res = get_access_token(modobio_id,encrypted_clinic_id, proxy_ds_user_id,encrypted_user_id)
        res_json = res.json()
        if res.ok:
            access_token = res_json['access_token']
            headers = {'Authorization': f'Bearer {access_token}'}
        else:
            raise BadRequest(f'DoseSpot returned the following error: {res_json}.')

        res = requests.get(f'https://my.staging.dosespot.com/webapi/api/patients/{ds_patient.ds_user_id}/prescriptions?startDate={start_date}&endDate={end_date}',
                headers=headers)
        res_json = res.json()
        if not res.ok:
            raise BadRequest(f'DoseSpot returned the following error: {res_json}.')

        if 'Items' not in res_json:
            raise BadRequest(f'DoseSpot may have changed their API output, please reach out to a staff admin.')

        lookup_users = lookup_ds_users()

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

        payload = {'items': res_json['Items'],
                   'total_items': len(res_json['Items'])}

        return payload

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
class DoseSpotEnrollmentStatus(BaseResource):
    @token_auth.login_required(user_type=('staff',),staff_role=('medical_doctor',))
    @responds(schema=DoseSpotEnrollmentGET,status_code=200, api=ns)
    def get(self, user_id):
        """
        GET - Only a ModoBio Practitioners will be able to use this endpoint. This endpoint is used
              to return their enrollment status
        """

        ds_practitioner = DoseSpotPractitionerID.query.filter_by(user_id=user_id).one_or_none()
        if not ds_practitioner:
            raise BadRequest('This practitioner does not have a DoseSpot account.')
        
        if ds_practitioner.ds_enrollment_status == 'enrolled':
            return {'status': ds_practitioner.ds_enrollment_status}

        admin_id = str(current_app.config['DOSESPOT_ADMIN_ID'])
        clinic_api_key = current_app.config['DOSESPOT_API_KEY']
        modobio_id = str(current_app.config['DOSESPOT_MODOBIO_ID'])

        # generating keys for ADMIN
        encrypted_clinic_id = current_app.config['DOSESPOT_ENCRYPTED_MODOBIO_ID']
        encrypted_user_id = generate_encrypted_user_id(encrypted_clinic_id[:22],clinic_api_key,admin_id)    

        res = get_access_token(modobio_id,encrypted_clinic_id,admin_id,encrypted_user_id)
        res_json = res.json()
        if res.ok:
            access_token = res_json['access_token']
            headers = {'Authorization': f'Bearer {access_token}'}
        else:
            raise BadRequest(f'DoseSpot returned the following error: {res_json}.')

        res = requests.get(f'https://my.staging.dosespot.com/webapi/api/clinicians/{ds_practitioner.ds_user_id}',headers=headers)
        res_json = res.json()
        if res.ok:
            # Confirmed = True means DoseSpot has verified the NPI number            
            if res_json['Item']!=0:
                if res_json['Item']['Confirmed'] == True:
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
        res_json = res.json()
        if res.ok:
            access_token = res_json['access_token']
            headers = {'Authorization': f'Bearer {access_token}'}
        else:
            raise BadRequest(f'DoseSpot returned the following error: {res_json}.')

        user = User.query.filter_by(user_id=user_id).one_or_none()
        state = LookupTerritoriesOfOperations.query.filter_by(idx=user.client_info.territory_id).one_or_none()

        res = requests.get(f'https://my.staging.dosespot.com/webapi/api/pharmacies/search?zip={user.client_info.zipcode}&state={state.sub_territory_abbreviation}',headers=headers)
        res_json = res.json()
        if not res.ok:
            raise BadRequest(f'DoseSpot returned the following error: {res_json}.')
        return res_json['Items']

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

        proxy_ds_user_id = str(current_app.config['DOSESPOT_PROXY_USER_ID'])         
        encrypted_user_id = generate_encrypted_user_id(encrypted_clinic_id[:22],clinic_api_key, proxy_ds_user_id)

        res = get_access_token(modobio_id,encrypted_clinic_id, proxy_ds_user_id,encrypted_user_id)

        res_json = res.json()
        if res.ok:
            access_token = res_json['access_token']
            headers = {'Authorization': f'Bearer {access_token}'}
        else:
            raise BadRequest(f'DoseSpot returned the following error: {res_json}.')

        res = requests.get(f'https://my.staging.dosespot.com/webapi/api/patients/{ds_patient.ds_user_id}/pharmacies',headers=headers)
        res_json = res.json()
        if not res.ok:
            raise BadRequest(f'DoseSpot returned the following error: {res_json}.')
        return res_json['Items']

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
