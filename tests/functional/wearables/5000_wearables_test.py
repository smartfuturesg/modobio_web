from flask.json import dumps

from odyssey.api.wearables.models import Wearables

from .data import wearables_data

def test_wearables_post(test_client):
    response = test_client.post(
        f'/wearables/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(wearables_data),
        content_type='application/json')

    assert response.status_code == 201

    data = Wearables.query.filter_by(user_id=test_client.client_id).first()

    assert data
    assert data.has_freestyle
    assert data.has_oura
    assert not data.registered_oura

def test_wearables_get(test_client):
    response = test_client.get(
        f'/wearables/{test_client.client_id}/',
        headers=test_client.client_auth_header)

    assert response.status_code == 200
    assert response.json == wearables_data

def test_wearables_put(test_client):
    new_data = wearables_data.copy()
    new_data['has_oura'] = False

    response = test_client.put(
        f'/wearables/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(new_data),
        content_type='application/json')

    assert response.status_code == 204

    data = Wearables.query.filter_by(user_id=test_client.client_id).first()

    assert data.has_freestyle
    assert not data.has_oura
