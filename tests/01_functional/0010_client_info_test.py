import pathlib
import time
from datetime import datetime

from flask.json import dumps
from requests.auth import _basic_auth_str

from odyssey.models.user import User, UserLogin
from odyssey.models.client import (
    ClientInfo,
    ClientConsent
)

from tests.data import (
    test_new_client_info,
    signature,
    test_client_consent_data,
    test_client_release_data,
    test_client_policies_data,
    test_client_consult_data,
    test_client_subscription_data,
    test_client_individual_data,
    test_new_user_client
)

def test_get_client_info(test_client, init_database):
    """
    GIVEN a api end point for retrieving client info
    WHEN the '/client/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on user_id = 1 
    response = test_client.get('/client/1/', headers=headers)

    # some simple checks for validity
    assert response.status_code == 200
    assert response.json['user_id'] == 1
    assert response.json['modobio_id']

def test_put_client_info(test_client, init_database):
    """
    GIVEN a api end point for retrieving client info
    WHEN the '/client/<client id>' resource  is requested to be changed (PUT)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # test attempting to change the user_id
    data = {'user_id': 10}
    # send get request for client info on user_id = 1 
    response = test_client.put('/client/1/', headers=headers, data=dumps(data),  content_type='application/json')

    assert response.status_code == 400
    assert response.json['message'] == 'Illegal Setting of parameter, user_id. You cannot set this value manually'

    # test attempting to change the phone number
    data = {'guardianname': 'Testy'}

    response = test_client.put('/client/1/', 
                                headers=headers, 
                                data=dumps(data),  
                                content_type='application/json')
    
    #load the client from the database

    client = ClientInfo.query.filter_by(user_id=1).one_or_none()
    assert response.status_code == 200
    assert client.guardianname == data['guardianname']

def test_creating_new_client(test_client, init_database):
    """
    GIVEN a api end point for retrieving client info
    WHEN the '/client/<client id>' resource  is requested to be changed (PUT)
    THEN check the response is valid
    """

    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = {'userinfo': test_new_user_client['userinfo'] }
    # send post request for a new client user account
    response = test_client.post('/user/client/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')

    user = User.query.filter_by(email=test_new_user_client['userinfo']['email']).first()
    assert response.status_code == 201
    assert user.email == test_new_user_client['userinfo']['email']
    assert response.json['modobio_id']


############
#Removing client is temporarily disabled until a better user deletion system is created
############

# def test_removing_client(test_client, init_database):
#     """
#     GIVEN a api end point for retrieving client info
#     WHEN the '/client/remove/<user_id>' resource  is requested to be changed (DELETE)
#     THEN check the response is valid
#     """

#     # get staff authorization to view client data
#     staff = User.query.filter_by(is_staff=True).first()
#     staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
#     token = staffLogin.get_token()
#     headers = {'Authorization': f'Bearer {token}'}

#     # send post request to create client
#     test_client.post('/user/',
#                     headers=headers, 
#                     data=dumps(test_new_user_client_2["clientinfo"]), 
#                     content_type='application/json')
                    
#     client = User.query.filter_by(email=test_new_user_client_2["clientinfo"]['email']).first()
    
#     #take this new user_id
#     remove_user_id = client.user_id

#     response = test_client.delete(f'/client/remove/{remove_user_id}/',
#                                 headers=headers, 
#                                 content_type='application/json')
#     # some simple checks for validity
#     assert response.status_code == 200