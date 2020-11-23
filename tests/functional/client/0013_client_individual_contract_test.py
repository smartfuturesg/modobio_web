from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from .data import clients_individual_data

#Skipping this test, due to pytest hanging problem
import pytest
pytest.skip("Checking if this is the culprit", allow_module_level=True)

def test_post_client_individual_contract(test_client, init_database):
    """
    GIVEN a api end point for posting client individual contract
    WHEN the '/client/servicescontract/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = clients_individual_data
    # send get request for client info on user_id = 1 
    response = test_client.post('/client/servicescontract/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')
    assert response.status_code == 201
    assert response.json['doctor'] == clients_individual_data['doctor']

def test_get_client_individual_contract(test_client, init_database):
    """
    GIVEN a api end point for retrieving the client individual contract
    WHEN the '/client/servicescontract/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on user_id = 1 
    response = test_client.get('/client/servicescontract/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    assert response.json['doctor'] == True
    