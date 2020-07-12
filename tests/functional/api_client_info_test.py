import datetime
import os

from flask.json import dumps, loads
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
    test_client_consent_form,
    test_client_release_form,
    test_client_policies_form,
    test_client_consult_contract,
    test_client_subscription_contract,
    test_client_individual_contract,
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
    response = test_client.get('/api/client/1/', headers=headers)
    
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
    response = test_client.put('/api/client/1/', headers=headers, data=dumps(data),  content_type='application/json')

    assert response.status_code == 400
    assert response.json['message'] == 'Illegal Setting of parameter, clientid. You cannot set this value manually'

    # test attempting to change the phone number
    data = {'phone': '9123456789'}

    response = test_client.put('/api/client/1/', 
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
    token = staff.token
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on clientid = 1 
    response = test_client.post('/api/client/',
                                headers=headers, 
                                data=dumps(test_new_client_info), 
                                content_type='application/json')
    
    client = ClientInfo.query.filter_by(email=test_new_client_info['email']).first()

    # some simple checks for validity
    assert response.status_code == 201
    assert client.email == 'test_this_client_two@gmail.com'
    assert client.get_medical_record_hash() == 'TC21CAB50'


def test_home_registration(test_client, init_database):
    """
    GIVEN a set of api end points intended to handle several steps 
    WHEN the '/client/' resource  is requested to be changed (PUT)
    THEN check the response is valid
    """
    ##
    # 1) create client home registration portal by sending a post request to 
    #   /remoteregistration/new/
    ##
    #  get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.token
    headers = {'Authorization': f'Bearer {token}'}


    response = test_client.post('/api/client/remoteregistration/new/',
                                headers=headers, 
                                data=dumps(test_new_remote_registration), 
                                content_type='application/json')

    password = response.json.get('password')
    tmp_registration_code = response.json.get('registration_portal_id')
    client = ClientInfo.query.filter_by(email=test_new_remote_registration['email']).first()

    assert response.status_code == 201
    assert client.email == test_new_remote_registration['email']

    ##
    # 2) get login to portal with temporary credentials to retrieve api token
    #   /remoteregistration/<string:tmp_registration>/
    ##

    credentials =_basic_auth_str(client.email, password)
    headers = {'Authorization': credentials}

    response = test_client.post(f'api/tokens/remoteregistration/{tmp_registration_code}/',
                                headers=headers, 
                                content_type='application/json')

    # client_token = response.json['token']

    assert response.status_code == 201

def test_get_client_consent(test_client, init_database):
    """
    GIVEN an api endpoint for retrieving client consent form
    WHEN the '/client/consent/<client id>' resource is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on clientid = 1
    response = test_client.get('/api/client/consent/1/', headers=headers)

    # some simple checks for validity
    assert response.status_code == 200

    response_data = dict(response.json)
    response_data.pop('clientid')

    expected_data = test_client_consent_form.copy()
    expected_data['signdate'] = expected_data['signdate'].isoformat()
    assert response_data == expected_data

def test_post_client_consent(test_client, init_database):
    """
    GIVEN an api endpoint for sending client consent form data
    WHEN the '/client/consent/<client id>' resource is sent data (POST)
    THEN check the response is valid and data is propagated
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # API POST request has not run yet, no PDF should exist
    consent = ClientConsent.query.filter_by(clientid=1).first()
    assert not consent.url

    # Run put request
    data = test_client_consent_form.copy()
    data['signdate'] = data['signdate'].isoformat()
    response = test_client.post('/api/client/consent/1/',
                                headers=headers,
                                data=dumps(data),
                                content_type='application/json')

    # Test response OK
    # Test that data was set correctly in the database
    # Test that PDF URL exists after post request was run
    # Test that URL points to existing file
    print(response.json['message'])
    assert response.status_code == 200
    assert consent.signdate == test_client_consent_form['signdate']
    assert consent.url
    assert os.path.exists(consent.url)
