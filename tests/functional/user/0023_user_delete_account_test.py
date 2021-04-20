import base64
import pathlib
import time
from datetime import datetime

from flask.json import dumps
from requests.auth import _basic_auth_str

from odyssey.api.user.models import User, UserLogin, UserRemovalRequests, UserPendingEmailVerifications
from odyssey.api.doctor.models import MedicalImaging
from odyssey.api.client.models import (
    ClientInfo,
    ClientConsent
)
from tests.functional.user.data import (
        users_to_delete_data, 
        users_new_self_registered_client_data
)
from tests.functional.doctor.data import doctor_medical_imaging_data
from odyssey import db

def test_account_delete_request(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for deleting a user
    WHEN the 'DELETE /user/{user_id}' resource  is requested 
    THEN check the response is valid
    """

    #Just need two users added to db, one client and one staff/client
    #1. Create self created client user
    payload = users_to_delete_data['client_user']
    client_user = test_client.post('/user/client/', 
            data=dumps(payload), 
            content_type='application/json')
    client_id = client_user.json['user_info']['user_id']
    
    #2. Create staff/cient user
    payload = users_to_delete_data['staff_client_user']
    test_client.post('/user/staff/',
            headers=staff_auth_header, 
            data=dumps(payload),
            content_type='application/json')
    staff_client_user = test_client.post('/user/client/',
            data=dumps(payload['user_info']),
            content_type='application/json')
    
    staff_client_id = staff_client_user.json['user_info']['user_id']

    #verify newly created staff member's email
    token = UserPendingEmailVerifications.query.filter_by(user_id=staff_client_id).first().token
    request = test_client.post(f'/user/email-verification/token/{token}/')
    token = UserPendingEmailVerifications.query.filter_by(user_id=staff_client_id).first().token
    request = test_client.post(f'/user/email-verification/token/{token}/')

    #3. Add info for client user, reported by staff/client
    valid_credentials = base64.b64encode(
            f"{payload['user_info']['email']}:{'password3'}".encode("utf-8")).decode("utf-8")
    headers = {'Authorization': f'Basic {valid_credentials}'}
    token_request_response = test_client.post('/staff/token/',
            headers=headers,
            content_type='application/json')
    token = token_request_response.json.get('token')
    
    staff_user_auth_header = {'Authorization': f'Bearer {token}'}

    payload = doctor_medical_imaging_data
    response = test_client.post(f'/doctor/images/{client_id}/',
            headers=staff_user_auth_header,
            data = payload)
    assert response.status_code == 201
    
    #4. Delete staff/client
    deleting_staff_client = test_client.delete(f'/user/{staff_client_id}/',
            headers=staff_user_auth_header)

    assert deleting_staff_client.status_code == 200
    assert deleting_staff_client.json['message'] == f"User with id {staff_client_id} has been removed"
    
    #Check no info for user_id is in staff tables
    tableList = db.session.execute("SELECT distinct(table_name) from information_schema.columns\
                WHERE table_name like 'Staff%';").fetchall()
                
    for table in tableList:
        exists = db.session.execute("SELECT EXISTS(SELECT * from \"{}\" WHERE user_id={});".format(table.table_name, staff_client_id))
        result = exists.fetchall().pop()
        assert result[0] == False
    assert tableList

    #   -Check info reported by staff user on client user is still in db
    med_imaging_record = MedicalImaging.query.filter_by(user_id=client_id).first()
    assert med_imaging_record
    assert med_imaging_record.user_id == client_id
    assert med_imaging_record.reporter_id == staff_client_id

    #   -Check modobioid, userid, name, email are in User table, no phone#
    staff_user = User.query.filter_by(user_id=staff_client_id).first()
    assert staff_user.phone_number == None
    assert staff_user.modobio_id
    assert staff_user.user_id
    assert staff_user.firstname
    assert staff_user.lastname
    assert staff_user.email

    #5. Delete client
    deleting_client = test_client.delete(f'/user/{client_id}/',
                headers=staff_auth_header)
    assert deleting_client.status_code == 200

    #   -Check only modobioid and userid are in User table
    client_user = User.query.filter_by(user_id=client_id).first()
    assert client_user.firstname == None
    assert client_user.lastname == None
    assert client_user.email == None
    assert client_user.phone_number == None
    assert client_user.modobio_id
    assert client_user.user_id

    #   -Check UserRemovalRequests tables is populated correctly
    removal_request = UserRemovalRequests.query.all()
    assert removal_request[0].user_id == staff_client_id
    assert removal_request[0].requester_user_id == staff_client_id
    assert removal_request[1].user_id == client_id
    #requester is the staff member created in conftest
    assert removal_request[1].requester_user_id == 2


    
