import base64
import pathlib
import time
from datetime import datetime

from flask.json import dumps
from requests.auth import _basic_auth_str

from odyssey.api.user.models import User, UserLogin
from odyssey.api.client.models import (
    ClientInfo,
    ClientConsent
)
from tests.functional.user.data import users_new_user_client_data, users_new_self_registered_client_data

#Skipping this test
import pytest
pytest.skip("Checking if this is the culprit", allow_module_level=True)

def test_account_delete_request_self(test_client, init_database):
    """
    GIVEN a api end point for regitering a new user client
    WHEN the 'user/client/' resource  is requested 
    THEN check the response is valid
    """
    #TODO test a client requesting account to delete:
    #1.create a client, add info to profile and other tables
    #2.delete client, we will only keep modobio and user id's, all other info is deleted.
    
    #TODO test a staff requesting account delete:
    #1.Create staff memeber, add info to profile and add info for a client as reporter
    #2.Delete staff, we will keep name, email, modobio and user ids
    #3.If the user_id is used as a reporter user id, we will keep that line.
    
    #TODO test a staff&client account delete:
    #1.Create an account that is both staff and client
    #2. Delete account
    #3.We will keep staff info, but delete client info.

    # We don't need a staff to be logged-in for a client to self-register
    payload = {'userinfo': users_new_self_registered_client_data['userinfo'] }
    
    # send post request for a new client user account
    response = test_client.post('/user/client/', 
                                data=dumps(payload), 
                                content_type='application/json')

    user = User.query.filter_by(email=payload['userinfo']['email']).first()
    assert response.status_code == 201
    assert user.email == users_new_self_registered_client_data['userinfo']['email']
    assert response.json['modobio_id']

    #Test token generation
    password = response.json['password']
    valid_credentials = base64.b64encode(
            f"{users_new_self_registered_client_data['userinfo']['email']}:{password}".encode("utf-8")).decode("utf-8")
    
    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post('/client/token/',
                            headers=headers, 
                            content_type='application/json')
    assert response.status_code == 201
    assert response.json['email'] == users_new_self_registered_client_data['userinfo']['email']

    #Test using wrong password
    password = 'thewrongpassword?'
    valid_credentials = base64.b64encode(
            f"{users_new_self_registered_client_data['userinfo']['email']}:{password}".encode("utf-8")).decode("utf-8")
    
    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post('/client/token/',
                            headers=headers, 
                            content_type='application/json')

    assert response.status_code == 401

def test_account_delete_request_other(test_client, init_database):
    """
    GIVEN a api end point for regitering a new user client
    WHEN the 'user/client/' resource  is requested 
    THEN check the response is valid
    """

    # We don't need a staff to be logged-in for a client to self-register
    payload = {'userinfo': users_new_self_registered_client_data['userinfo'] }
    
    # send post request for a new client user account
    response = test_client.post('/user/client/', 
                                data=dumps(payload), 
                                content_type='application/json')

    user = User.query.filter_by(email=payload['userinfo']['email']).first()
    assert response.status_code == 201
    assert user.email == users_new_self_registered_client_data['userinfo']['email']
    assert response.json['modobio_id']

    #Test token generation
    password = response.json['password']
    valid_credentials = base64.b64encode(
            f"{users_new_self_registered_client_data['userinfo']['email']}:{password}".encode("utf-8")).decode("utf-8")
    
    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post('/client/token/',
                            headers=headers, 
                            content_type='application/json')
    assert response.status_code == 201
    assert response.json['email'] == users_new_self_registered_client_data['userinfo']['email']

    #Test using wrong password
    password = 'thewrongpassword?'
    valid_credentials = base64.b64encode(
            f"{users_new_self_registered_client_data['userinfo']['email']}:{password}".encode("utf-8")).decode("utf-8")
    
    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post('/client/token/',
                            headers=headers, 
                            content_type='application/json')

    assert response.status_code == 401