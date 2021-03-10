from flask.json import dumps

from odyssey.api.wearables.models import Wearables

from .data import wearables_data

def test_wearables_post(test_client, init_database, client_auth_header):
    """
    GIVEN an API end point for wearable devices
    WHEN the '/wearables/<user_id>' resource is requested (POST)
    THEN check the response is valid
    """

    response = test_client.post(
        '/wearables/1/',
        headers=client_auth_header,
        data=dumps(wearables_data),
        content_type='application/json'
    )

    assert response.status_code == 201

    data = Wearables.query.filter_by(user_id=1).first()

    assert data
    assert data.has_freestyle
    assert data.has_oura
    assert not data.registered_oura

def test_wearables_get(test_client, init_database, client_auth_header):
    """
    GIVEN an API end point for wearable devices
    WHEN the '/wearables/<user_id>' resource is requested (GET)
    THEN check the response is valid
    """

    response = test_client.get(
        '/wearables/1/',
        headers=client_auth_header
    )

    assert response.status_code == 200
    assert response.json == wearables_data

def test_wearables_put(test_client, init_database, client_auth_header):
    """
    GIVEN an API end point for wearable devices
    WHEN the '/wearables/<user_id>' resource is requested (PUT)
    THEN check the response is valid
    """

    new_data = wearables_data.copy()
    new_data['has_oura'] = False

    response = test_client.put(
        '/wearables/1/',
        headers=client_auth_header,
        data=dumps(new_data),
        content_type='application/json'
    )

    assert response.status_code == 204

    data = Wearables.query.filter_by(user_id=1).first()

    assert data.has_freestyle
    assert not data.has_oura

