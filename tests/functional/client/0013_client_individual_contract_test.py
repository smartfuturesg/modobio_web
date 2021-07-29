from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from .data import clients_individual_data

def test_post_client_individual_contract(test_client):
    payload = clients_individual_data
    response = test_client.post(
        f'/client/servicescontract/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['doctor'] == clients_individual_data['doctor']

def test_get_client_individual_contract(test_client):
    response = test_client.get(
        f'/client/servicescontract/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['doctor'] == True
