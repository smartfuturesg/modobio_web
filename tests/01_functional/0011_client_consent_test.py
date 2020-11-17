import time 

from flask.json import dumps

from odyssey.models.user import User, UserLogin
from tests.data.clients.clients_data import (
    clients_consent_data
)

def test_post_client_consent(test_client, init_database):
    """
    GIVEN a api end point for posting client consent
    WHEN the '/client/consent/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = clients_consent_data
    # send get request for client info on user_id = 1 
    response = test_client.post('/client/consent/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')
    #wait for pdf generation
    time.sleep(3)
    assert response.status_code == 201
    assert response.json['infectious_disease'] == clients_consent_data['infectious_disease']

def test_get_client_consent(test_client, init_database):
    """
    GIVEN a api end point for retrieving the client consent
    WHEN the '/client/consent/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on user_id = 1 
    response = test_client.get('/client/consent/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    assert response.json['infectious_disease'] == False
    