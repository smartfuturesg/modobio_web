import time

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from .data import clients_consent_data

def test_post_client_consent(test_client):
    payload = clients_consent_data
    response = test_client.post(f'/client/consent/{test_client.client_id}/',
                                headers=test_client.staff_auth_header,
                                data=dumps(payload),
                                content_type='application/json')
    #wait for pdf generation
    time.sleep(3)
    assert response.status_code == 201
    assert response.json['infectious_disease'] == clients_consent_data['infectious_disease']

def test_get_client_consent(test_client):
    response = test_client.get(f'/client/consent/{test_client.client_id}/',
                                headers=test_client.staff_auth_header,
                                content_type='application/json')
    assert response.status_code == 200
    assert response.json['infectious_disease'] == False
