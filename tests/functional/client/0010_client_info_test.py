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
from tests.functional.client.data import client_info_put_test_data
from tests.functional.user.data import users_new_user_client_data


def test_get_client_info(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for retrieving client info
    WHEN the '/client/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    

    # send get request for client info on user_id = 1 
    response = test_client.get('/client/1/', headers=staff_auth_header)
    
    # some simple checks for validity
    assert response.status_code == 200
    assert response.json['user_info']['user_id'] == 1
    assert response.json['user_info']['modobio_id']

def test_put_client_info(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for retrieving client info
    WHEN the '/client/<client id>' resource  is requested to be changed (PUT)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    

    # test attempting to change the user_id
    data = {'client_info': {'user_id': 10}}
    # send get request for client info on user_id = 1 
    response = test_client.put('/client/1/', headers=staff_auth_header, data=dumps(data),  content_type='application/json')

    assert response.status_code == 400

    # test attempting to change the guardian name
    data = {'client_info': {'guardianname': 'Testy'}}

    response = test_client.put('/client/1/', 
                                headers=staff_auth_header, 
                                data=dumps(data),  
                                content_type='application/json')
    
    #load the client from the database
    client = ClientInfo.query.filter_by(user_id=1).one_or_none()
    assert response.status_code == 200
    assert client.guardianname == 'Testy'

    # test full payload of updates to client info data
    response = test_client.put('/client/1/', 
                            headers=staff_auth_header, 
                            data=dumps(client_info_put_test_data),  
                            content_type='application/json')
    
    assert response.status_code == 200
    assert response.json["client_info"]["primary_goal"] == "('Recovery',)"
    assert response.json["client_info"]["race"] == "('White / Caucasian',)"
    assert response.json["client_info"]["race_id"] == 1
    assert response.json["client_info"]["primary_goal_id"] == 1

def test_creating_new_client(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for retrieving client info
    WHEN the '/client/<client id>' resource  is requested to be changed (PUT)
    THEN check the response is valid
    """
    
    payload = users_new_user_client_data['user_info']
    
    # send post request for a new client user account
    response = test_client.post('/user/client/',
                                headers=staff_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')

    user = User.query.filter_by(email=users_new_user_client_data['user_info']['email']).first()
    
    assert response.status_code == 201
    assert user.email == users_new_user_client_data['user_info']['email']
    assert response.json['user_info']['modobio_id']

    ###############
    # Use generated password to test token generation
    # 1) correct password
    # 2) Incorrect password
    ###############
    password = payload['password']
    valid_credentials = base64.b64encode(
            f"{users_new_user_client_data['user_info']['email']}:{password}".encode("utf-8")).decode("utf-8")
    
    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post('/client/token/',
                            headers=headers, 
                            content_type='application/json')
    assert response.status_code == 201
    assert response.json['email'] == users_new_user_client_data['user_info']['email']


    password = 'thewrongpassword?'
    valid_credentials = base64.b64encode(
            f"{users_new_user_client_data['user_info']['email']}:{password}".encode("utf-8")).decode("utf-8")
    
    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post('/client/token/',
                            headers=headers, 
                            content_type='application/json')

    assert response.status_code == 401
