import datetime
import pathlib
import time

from flask.json import dumps
from requests.auth import _basic_auth_str

from odyssey.models.main import Staff
from odyssey.models.intake import (
    ClientInfo,
    ClientConsent
)

from tests.data import (
    test_new_client_info,
    test_new_remote_registration,
    signature,
    test_client_consent_data,
    test_client_release_data,
    test_client_policies_data,
    test_client_consult_data,
    test_client_subscription_data,
    test_client_individual_data,
)

def test_get_client_info(test_client, init_database):
    """
    GIVEN a api end point for retrieving client info
    WHEN the '/client/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on clientid = 1 
    response = test_client.get('/client/1/', headers=headers)
    # some simple checks for validity
    
    assert response.status_code == 200
    assert response.json['clientid'] == 1
    assert response.json['email'] == 'test_this_client@gmail.com'
    assert response.json['record_locator_id'] == 'TC148FAC4'

def test_put_client_info(test_client, init_database):
    """
    GIVEN a api end point for retrieving client info
    WHEN the '/client/<client id>' resource  is requested to be changed (PUT)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # test attempting to change the clientid
    data = {'clientid': 10}
    # send get request for client info on clientid = 1 
    response = test_client.put('/client/1/', headers=headers, data=dumps(data),  content_type='application/json')

    assert response.status_code == 400
    assert response.json['message'] == 'Illegal Setting of parameter, clientid. You cannot set this value manually'

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
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on clientid = 1 
    response = test_client.post('/client/',
                                headers=headers, 
                                data=dumps(test_new_client_info), 
                                content_type='application/json')
    client = ClientInfo.query.filter_by(email=test_new_client_info['email']).first()
    # some simple checks for validity
    assert response.status_code == 201
    assert client.email == 'test_this_client_two@gmail.com'
    assert client.get_medical_record_hash() == 'TC21CAB50'

def test_removing_client(test_client, init_database):
    """
    GIVEN a api end point for retrieving client info
    WHEN the '/client/remove/<client id>' resource  is requested to be changed (DELETE)
    THEN check the response is valid
    """

    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send post request to create client
    test_client.post('/client/',
                    headers=headers, 
                    data=dumps(test_new_client_info), 
                    content_type='application/json')
                    
    client = ClientInfo.query.filter_by(email=test_new_client_info['email']).first()
    
    #take this new clientid
    remove_clientid = client.clientid

    response = test_client.delete(f'/client/remove/{remove_clientid}/',
                                headers=headers, 
                                content_type='application/json')
    # some simple checks for validity
    assert response.status_code == 200

