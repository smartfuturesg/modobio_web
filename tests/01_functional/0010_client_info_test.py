import pathlib
import time

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
    assert response.json['email'] == 'test_this_client@gmail.com'

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
    data = {'phone': '9123456789'}

    response = test_client.put('/client/1/', 
                                headers=headers, 
                                data=dumps(data),  
                                content_type='application/json')
    
    #load the client from the database

    client = ClientInfo().query.first()

    assert response.status_code == 200
    assert client.phone == data['phone']

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

    # send post request for a new client user account
    response = test_client.post('/user/',
                                headers=headers, 
                                data=dumps(test_new_user_client['userinfo']), 
                                content_type='application/json')
    user = User.query.filter_by(email=test_new_user_client['userinfo']['email']).first()
    assert response.status_code == 201
    assert user.email == 'test_this_client_two@gmail.com'

    #send put request to fill out ClientInfo table for new user
    test_new_user_client['clientinfo']['user_id'] = user.user_id
    response = test_client.put('/client/',
                                headers=headers,
                                data=dumps(test_new_user_client["clientinfo"]),
                                content_type='application/json')
    client = ClientInfo.query.filter_by(user_id=user.user_id).first()

    # some simple checks for validity
    assert response.status_code == 201
    assert client.dob == '1991-10-14'

def test_removing_client(test_client, init_database):
    """
    GIVEN a api end point for retrieving client info
    WHEN the '/client/remove/<user_id>' resource  is requested to be changed (DELETE)
    THEN check the response is valid
    """

    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send post request to create client
    test_client.post('/client/',
                    headers=headers, 
                    data=dumps(test_new_client_info), 
                    content_type='application/json')
                    
    client = ClientInfo.query.filter_by(email=test_new_client_info['email']).first()
    
    #take this new user_id
    remove_user_id = client.user_id

    response = test_client.delete(f'/client/remove/{remove_user_id}/',
                                headers=headers, 
                                content_type='application/json')
    # some simple checks for validity
    assert response.status_code == 200