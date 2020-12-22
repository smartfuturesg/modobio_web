import base64
import pathlib
import time
from datetime import datetime

from flask.json import dumps
from requests.auth import _basic_auth_str

from odyssey.api.user.models import User, UserLogin
from odyssey.api.doctor.models import MedicalImaging
from odyssey.api.client.models import (
    ClientInfo,
    ClientConsent
)
from tests.functional.user.data import users_to_delete_data, users_new_self_registered_client_data
from tests.functional.doctor.data import doctor_medical_imaging_data

def test_account_delete_request(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for deleting a user
    WHEN the 'DELETE /user/{user_id}' resource  is requested 
    THEN check the response is valid
    """

    #Just need two users added to db, one client and one staff/client
    #1. Create self created client user
    payload = users_to_delete_data['client_user']
    client_user = test_client.post(
            '/user/client/', 
            data=dumps(payload), 
            content_type='application/json')
    client_id = client_user.json['user_id']
    
    #2. Create staff/cient user
    payload = users_to_delete_data['staff_client_user']
    staff_user = test_client.post(
            '/user/staff/',
            headers=staff_auth_header, 
            data=dumps(payload),
            content_type='application/json')
    staff_client_user = test_client.post(
            '/user/client/',
            data=dumps(payload['user_info']),
            content_type='application/json')
    
    staff_client_id = staff_client_user.json['user_id']
    #3. Add info for client user, reported by staff/client
    valid_credentials = base64.b64encode(
            f"{payload['user_info']['email']}:{'password3'}".encode("utf-8")).decode("utf-8")
    headers = {'Authorization': f'Basic {valid_credentials}'}
    token_request_response = test_client.post(
            '/staff/token/',
            headers=headers,
            content_type='application/json')
    token = token_request_response.json.get('token')
    
    staff_user_auth_header = {'Authorization': f'Bearer {token}'}

    payload = doctor_medical_imaging_data
    response = test_client.post(
            f'/doctor/images/{client_id}/',
            headers=staff_user_auth_header,
            data = payload)
    med_imaging_record = MedicalImaging.query.filter_by(user_id=client_id).first()
    assert med_imaging_record
    assert med_imaging_record.reporter_id == staff_client_id
    #4. Add staff info for staff/client user
    #5. Delete staff/client
    #   -Check no info for user_id is in staff tables
    #   -Check info reported by staff user on client user is still in db
    #   -Check modobioid, userid, name, email are in User table, no phone#
    #6. Delete client
    #   -Check only modobioid and userid are in User table
    #   -Check UserRemovalRequests tables is populated correctly

    
