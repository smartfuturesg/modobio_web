from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from .data import clients_release_data

def test_post_client_release(test_client):
    payload = clients_release_data
    response = test_client.post(f'/client/release/{test_client.client_id}/',
                                headers=test_client.client_auth_header,
                                data=dumps(payload),
                                content_type='application/json')
    assert response.status_code == 201
    assert response.json['release_of_other'] == clients_release_data['release_of_other']
    assert response.json['release_to'][0]['email'] == clients_release_data['release_to'][0]['email']

def test_get_client_release(test_client):
    response = test_client.get(f'/client/release/{test_client.client_id}/',
                                headers=test_client.client_auth_header,
                                content_type='application/json')

    assert response.status_code == 200
    assert response.json['release_of_other'] == 'Only release my prescription drugs, not anything else.'
