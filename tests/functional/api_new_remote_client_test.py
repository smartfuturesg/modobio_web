import datetime
import pathlib
import time

from flask.json import dumps
from requests.auth import _basic_auth_str

from odyssey.models.main import Staff
from odyssey.models.intake import (
    ClientInfo,
    RemoteRegistration
)

from tests.data import (
    test_new_remote_registration,
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

