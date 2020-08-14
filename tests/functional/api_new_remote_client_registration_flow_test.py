import base64
import datetime
import pathlib
import time

from flask.json import dumps
from requests.auth import _basic_auth_str

from odyssey.models.staff import Staff
from odyssey.models.client import (
    ClientInfo,
    RemoteRegistration
)

from tests.data import (
    test_new_remote_registration,
    test_new_client_info,
    test_medical_history,
    test_pt_history,
    test_client_consent_data,
    test_client_release_data,
    test_client_policies_data,
    test_client_subscription_data,
    test_client_individual_data,
    test_client_consult_data
)


def test_creating_new_remote_client(test_client, init_database):
    """
    GIVEN a api end point for creating a new client at home registration 
    WHEN the '/client/remoteregistration/new' resource  is requested to be changed (PUT)
    THEN check the response is valid
    """

    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    response = test_client.post('/client/remoteregistration/new/',
                                headers=headers, 
                                data=dumps(test_new_remote_registration), 
                                content_type='application/json')
    
    #the new client should be in the ClientInfo database 
    client = ClientInfo.query.filter_by(email=test_new_remote_registration['email']).first()
    
    remote_client = RemoteRegistration.query.filter_by(email=test_new_remote_registration['email']).first()
    
    # some simple checks for validity
    assert response.status_code == 201
    assert client.email == 'rest_remote_registration@gmail.com'
    assert remote_client.email == 'rest_remote_registration@gmail.com'

def test_refresh_new_remote_client_session(test_client, init_database):
    """
    GIVEN a api end point for creating a new client at home registration 
    WHEN the '/client/remoteregistration/new' resource  is requested to be changed (PUT)
    THEN check the response is valid
    """

    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    payload = {'email': test_new_remote_registration['email']}
    response = test_client.post('/client/remoteregistration/refresh/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 201

#############
# The following tests will be from the client side of the remote registration
#############

def test_get_remote_client_api_token(test_client, init_database):
    """
    GIVEN a api end point for getting a remote client api access token 
    WHEN the '/tokens/remoteregistration/' resource  is requested to be changed (POST)
    THEN check the response is valid
    """
    # bring up the client to get password
    remote_client = RemoteRegistration.query.filter_by(
                        email=test_new_remote_registration['email']).order_by(
                        RemoteRegistration.idx.desc()).first()
    
    tmp_registration = remote_client.registration_portal_id
    valid_credentials = base64.b64encode(f"{remote_client.email}:{remote_client.password}".encode("utf-8")).decode("utf-8")
    
    headers = {'Authorization': f'Basic {valid_credentials}'}
    
    
    response = test_client.post(f"/tokens/remoteregistration/?tmp_registration={tmp_registration}",
                                headers=headers, 
                                content_type='application/json')

    assert response.status_code == 201


def test_client_info_remote_client_session(test_client, init_database):
    """
    GIVEN a api end point for creating a new client at home registration 
    WHEN the '/remoteclient/clientinfo/' resource  is requested to be changed (PUT)
    THEN check the response is valid
    """

    remote_client = RemoteRegistration.query.filter_by(
                        email=test_new_remote_registration['email']).order_by(
                        RemoteRegistration.idx.desc()).first()

    tmp_registration = remote_client.registration_portal_id
    api_token = remote_client.token

    # get client authorization to view  data
    headers = {'Authorization': f'Bearer {api_token}'}
    
    payload = test_new_client_info
    payload['email'] = test_new_remote_registration['email']
    
    response = test_client.put(f"/remoteclient/clientinfo/?tmp_registration={tmp_registration}",
                                headers=headers, 
                                data=dumps(test_new_client_info), 
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 200

def test_medical_history_remote_client_session(test_client, init_database):
    """
    GIVEN a api end point for creating a new client at home registration 
    WHEN the '/remoteclient/medicalhistory/' resource  is requested to be created (POST)
    THEN check the response is valid
    """

    remote_client = RemoteRegistration.query.filter_by(
                        email=test_new_remote_registration['email']).order_by(
                        RemoteRegistration.idx.desc()).first()

    tmp_registration = remote_client.registration_portal_id
    api_token = remote_client.token

    # get client authorization to view  data
    headers = {'Authorization': f'Bearer {api_token}'}
    
    
    response = test_client.post(f"/remoteclient/medicalhistory/?tmp_registration={tmp_registration}",
                                headers=headers, 
                                data=dumps(test_medical_history), 
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 201

def test_put_medical_history_remote_client_session(test_client, init_database):
    """
    GIVEN a api end point for creating a new client at home registration 
    WHEN the '/remoteclient/medicalhistory/' resource  is requested to be changed (PUT)
    THEN check the response is valid
    """

    remote_client = RemoteRegistration.query.filter_by(
                        email=test_new_remote_registration['email']).order_by(
                        RemoteRegistration.idx.desc()).first()

    tmp_registration = remote_client.registration_portal_id
    api_token = remote_client.token

    # get client authorization to view  data
    headers = {'Authorization': f'Bearer {api_token}'}
    
    test_medical_history["allergies"] = "the sun"
    
    response = test_client.put(f"/remoteclient/medicalhistory/?tmp_registration={tmp_registration}",
                                headers=headers, 
                                data=dumps(test_medical_history), 
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 200
    assert response.json["allergies"] == "the sun" 

def test_get_medical_history_remote_client_session(test_client, init_database):
    """
    GIVEN a api end point for creating a new client at home registration 
    WHEN the '/remoteclient/medicalhistory/' resource  is requested (GET)
    THEN check the response is valid
    """

    remote_client = RemoteRegistration.query.filter_by(
                        email=test_new_remote_registration['email']).order_by(
                        RemoteRegistration.idx.desc()).first()

    tmp_registration = remote_client.registration_portal_id
    api_token = remote_client.token

    # get client authorization to view  data
    headers = {'Authorization': f'Bearer {api_token}'}
    
    
    response = test_client.get(f"/remoteclient/medicalhistory/?tmp_registration={tmp_registration}",
                                headers=headers, 
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 200

def test_pt_history_remote_client_session(test_client, init_database):
    """
    GIVEN a api end point for creating a new client at home registration 
    WHEN the '/remoteclient/pthistory/' resource  is requested to be created (POST)
    THEN check the response is valid
    """

    remote_client = RemoteRegistration.query.filter_by(
                        email=test_new_remote_registration['email']).order_by(
                        RemoteRegistration.idx.desc()).first()

    tmp_registration = remote_client.registration_portal_id
    api_token = remote_client.token

    # get client authorization to view  data
    headers = {'Authorization': f'Bearer {api_token}'}
    
    response = test_client.post(f"/remoteclient/pthistory/?tmp_registration={tmp_registration}",
                                headers=headers, 
                                data=dumps(test_pt_history), 
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 201

def test_get_pt_history_remote_client_session(test_client, init_database):
    """
    GIVEN a api end point for creating a new client at home registration 
    WHEN the '/remoteclient/pthistory/' resource  is requested (GET)
    THEN check the response is valid
    """

    remote_client = RemoteRegistration.query.filter_by(
                        email=test_new_remote_registration['email']).order_by(
                        RemoteRegistration.idx.desc()).first()

    tmp_registration = remote_client.registration_portal_id
    api_token = remote_client.token

    # get client authorization to view  data
    headers = {'Authorization': f'Bearer {api_token}'}
    
    response = test_client.get(f"/remoteclient/pthistory/?tmp_registration={tmp_registration}",
                                headers=headers, 
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 200

def test_put_pt_history_remote_client_session(test_client, init_database):
    """
    GIVEN a api end point for creating a new client at home registration 
    WHEN the '/remoteclient/pthistory/' resource  is requested to be changed (PUT)
    THEN check the response is valid
    """

    remote_client = RemoteRegistration.query.filter_by(
                        email=test_new_remote_registration['email']).order_by(
                        RemoteRegistration.idx.desc()).first()

    tmp_registration = remote_client.registration_portal_id
    api_token = remote_client.token

    # get client authorization to view  data
    headers = {'Authorization': f'Bearer {api_token}'}

    test_pt_history["exercise"] = "none, I give up"

    response = test_client.put(f"/remoteclient/pthistory/?tmp_registration={tmp_registration}",
                                headers=headers, 
                                data=dumps(test_pt_history), 
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 200
    assert response.json['exercise'] == "none, I give up"



def test_post_consent_client_session(test_client, init_database):
    """
    GIVEN a api end point for creating a signed doc
    WHEN the '/remoteclient/consent/' resource  is requested to be created (POST)
    THEN check the response is valid
    """

    remote_client = RemoteRegistration.query.filter_by(
                        email=test_new_remote_registration['email']).order_by(
                        RemoteRegistration.idx.desc()).first()

    tmp_registration = remote_client.registration_portal_id
    api_token = remote_client.token

    # get client authorization to view  data
    headers = {'Authorization': f'Bearer {api_token}'}
    
    response = test_client.post(f"/remoteclient/consent/?tmp_registration={tmp_registration}",
                                headers=headers, 
                                data=dumps(test_client_consent_data), 
                                content_type='application/json')
    # some simple checks for validity
    assert response.status_code == 201


def test_get_consent_client_session(test_client, init_database):
    """
    GIVEN a api end point getting a signed doc
    WHEN the '/remoteclient/consent/' resource  is requested to be created (GET)
    THEN check the response is valid
    """

    remote_client = RemoteRegistration.query.filter_by(
                        email=test_new_remote_registration['email']).order_by(
                        RemoteRegistration.idx.desc()).first()

    tmp_registration = remote_client.registration_portal_id
    api_token = remote_client.token

    # get client authorization to view  data
    headers = {'Authorization': f'Bearer {api_token}'}
    
    response = test_client.get(f"/remoteclient/consent/?tmp_registration={tmp_registration}",
                                headers=headers, 
                                content_type='application/json')
    # some simple checks for validity
    assert response.status_code == 200


def test_post_release_client_session(test_client, init_database):
    """
    GIVEN a api end point for creating a signed doc
    WHEN the '/remoteclient/release/' resource  is requested to be created (POST)
    THEN check the response is valid
    """

    remote_client = RemoteRegistration.query.filter_by(
                        email=test_new_remote_registration['email']).order_by(
                        RemoteRegistration.idx.desc()).first()

    tmp_registration = remote_client.registration_portal_id
    api_token = remote_client.token

    # get client authorization to view  data
    headers = {'Authorization': f'Bearer {api_token}'}
    
    response = test_client.post(f"/remoteclient/release/?tmp_registration={tmp_registration}",
                                headers=headers, 
                                data=dumps(test_client_release_data), 
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 201


def test_get_release_client_session(test_client, init_database):
    """
    GIVEN a api end point getting a signed doc
    WHEN the '/remoteclient/release/' resource  is requested to be created (GET)
    THEN check the response is valid
    """

    remote_client = RemoteRegistration.query.filter_by(
                        email=test_new_remote_registration['email']).order_by(
                        RemoteRegistration.idx.desc()).first()

    tmp_registration = remote_client.registration_portal_id
    api_token = remote_client.token

    # get client authorization to view  data
    headers = {'Authorization': f'Bearer {api_token}'}
    
    response = test_client.get(f"/remoteclient/release/?tmp_registration={tmp_registration}",
                                headers=headers, 
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 200


def test_post_policies_client_session(test_client, init_database):
    """
    GIVEN a api end point for creating a signed doc
    WHEN the '/remoteclient/policies/' resource  is requested to be created (POST)
    THEN check the response is valid
    """

    remote_client = RemoteRegistration.query.filter_by(
                        email=test_new_remote_registration['email']).order_by(
                        RemoteRegistration.idx.desc()).first()

    tmp_registration = remote_client.registration_portal_id
    api_token = remote_client.token

    # get client authorization to view  data
    headers = {'Authorization': f'Bearer {api_token}'}
    
    response = test_client.post(f"/remoteclient/policies/?tmp_registration={tmp_registration}",
                                headers=headers, 
                                data=dumps(test_client_policies_data), 
                                content_type='application/json')
                                
    # some simple checks for validity
    assert response.status_code == 201


def test_get_policies_client_session(test_client, init_database):
    """
    GIVEN a api end point getting a signed doc
    WHEN the '/remoteclient/policies/' resource  is requested  (GET)
    THEN check the response is valid
    """

    remote_client = RemoteRegistration.query.filter_by(
                        email=test_new_remote_registration['email']).order_by(
                        RemoteRegistration.idx.desc()).first()

    tmp_registration = remote_client.registration_portal_id
    api_token = remote_client.token

    # get client authorization to view  data
    headers = {'Authorization': f'Bearer {api_token}'}
    
    response = test_client.get(f"/remoteclient/policies/?tmp_registration={tmp_registration}",
                                headers=headers, 
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 200


def test_post_consult_client_session(test_client, init_database):
    """
    GIVEN a api end point for creating a signed doc
    WHEN the '/remoteclient/consultcontract/' resource  is requested to be created (POST)
    THEN check the response is valid
    """

    remote_client = RemoteRegistration.query.filter_by(
                        email=test_new_remote_registration['email']).order_by(
                        RemoteRegistration.idx.desc()).first()

    tmp_registration = remote_client.registration_portal_id
    api_token = remote_client.token

    # get client authorization to view  data
    headers = {'Authorization': f'Bearer {api_token}'}
    
    response = test_client.post(f"/remoteclient/consultcontract/?tmp_registration={tmp_registration}",
                                headers=headers, 
                                data=dumps(test_client_policies_data), 
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 201


def test_get_consult_client_session(test_client, init_database):
    """
    GIVEN a api end point getting a signed doc
    WHEN the '/remoteclient/consultcontract/' resource  is requested  (GET)
    THEN check the response is valid
    """

    remote_client = RemoteRegistration.query.filter_by(
                        email=test_new_remote_registration['email']).order_by(
                        RemoteRegistration.idx.desc()).first()

    tmp_registration = remote_client.registration_portal_id
    api_token = remote_client.token

    # get client authorization to view  data
    headers = {'Authorization': f'Bearer {api_token}'}
    
    response = test_client.get(f"/remoteclient/consultcontract/?tmp_registration={tmp_registration}",
                                headers=headers, 
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 200


def test_post_subscription_client_session(test_client, init_database):
    """
    GIVEN a api end point for creating a signed doc
    WHEN the '/remoteclient/subscriptioncontract/' resource  is requested to be created (POST)
    THEN check the response is valid
    """

    remote_client = RemoteRegistration.query.filter_by(
                        email=test_new_remote_registration['email']).order_by(
                        RemoteRegistration.idx.desc()).first()

    tmp_registration = remote_client.registration_portal_id
    api_token = remote_client.token

    # get client authorization to view  data
    headers = {'Authorization': f'Bearer {api_token}'}
    
    response = test_client.post(f"/remoteclient/subscriptioncontract/?tmp_registration={tmp_registration}",
                                headers=headers, 
                                data=dumps(test_client_subscription_data), 
                                content_type='application/json')
                                
    # some simple checks for validity
    assert response.status_code == 201


def test_get_subscription_client_session(test_client, init_database):
    """
    GIVEN a api end point getting a signed doc
    WHEN the '/remoteclient/subscriptioncontract/' resource  is requested  (GET)
    THEN check the response is valid
    """

    remote_client = RemoteRegistration.query.filter_by(
                        email=test_new_remote_registration['email']).order_by(
                        RemoteRegistration.idx.desc()).first()

    tmp_registration = remote_client.registration_portal_id
    api_token = remote_client.token

    # get client authorization to view  data
    headers = {'Authorization': f'Bearer {api_token}'}
    
    response = test_client.get(f"/remoteclient/subscriptioncontract/?tmp_registration={tmp_registration}",
                                headers=headers, 
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 200


def test_post_services_client_session(test_client, init_database):
    """
    GIVEN a api end point for creating a signed doc
    WHEN the '/remoteclient/servicescontract/' resource  is requested to be created (POST)
    THEN check the response is valid
    """

    remote_client = RemoteRegistration.query.filter_by(
                        email=test_new_remote_registration['email']).order_by(
                        RemoteRegistration.idx.desc()).first()

    tmp_registration = remote_client.registration_portal_id
    api_token = remote_client.token

    # get client authorization to view  data
    headers = {'Authorization': f'Bearer {api_token}'}
    
    response = test_client.post(f"/remoteclient/servicescontract/?tmp_registration={tmp_registration}",
                                headers=headers, 
                                data=dumps(test_client_individual_data), 
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 201


def test_get_services_client_session(test_client, init_database):
    """
    GIVEN a api end point getting a signed doc
    WHEN the '/remoteclient/servicescontract/' resource  is requested  (GET)
    THEN check the response is valid
    """

    remote_client = RemoteRegistration.query.filter_by(
                        email=test_new_remote_registration['email']).order_by(
                        RemoteRegistration.idx.desc()).first()

    tmp_registration = remote_client.registration_portal_id
    api_token = remote_client.token

    # get client authorization to view  data
    headers = {'Authorization': f'Bearer {api_token}'}
    
    response = test_client.get(f"/remoteclient/servicescontract/?tmp_registration={tmp_registration}",
                                headers=headers, 
                                content_type='application/json')
                                
    # some simple checks for validity
    assert response.status_code == 200


def test_get_signeddocs_client_session(test_client, init_database):
    """
    GIVEN a api end point getting a signed doc
    WHEN the '/remoteclient/signeddocuments/' resource  is requested  (GET)
    THEN check the response is valid
    """

    remote_client = RemoteRegistration.query.filter_by(
                        email=test_new_remote_registration['email']).order_by(
                        RemoteRegistration.idx.desc()).first()

    tmp_registration = remote_client.registration_portal_id
    api_token = remote_client.token

    # get client authorization to view  data
    headers = {'Authorization': f'Bearer {api_token}'}
    
    response = test_client.get(f"/remoteclient/signeddocuments/?tmp_registration={tmp_registration}",
                                headers=headers, 
                                content_type='application/json')

    # some simple checks for validity
    assert response.status_code == 200
