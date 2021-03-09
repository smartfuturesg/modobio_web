import pytest

from flask.json import dumps

from odyssey.api.wearables.models import Wearables, WearablesFitbit

from .data import wearables_data

def test_fitbit_pre_auth(test_client, init_database, client_auth_header):
    """
    GIVEN an API end point for Wearables general info
    WHEN the '/wearables/<user_id>' resource is requested (GET)
    THEN check the response is valid
    """
    data = Wearables.query.filter_by(user_id=1).one_or_none()

    # Not checking the data, just differentiating between PUT or POST
    if data:
        op = test_client.put
    else:
        op = test_client.post

    response = op(
        '/wearables/1/',
        headers=client_auth_header,
        data=dumps(wearables_data),
        content_type='application/json'
    )

    assert response.status_code in (201, 204)

    data = Wearables.query.filter_by(user_id=1).first()

    assert data
    assert data.has_fitbit
    assert not data.registered_fitbit

@pytest.mark.skip('AWS Parameter Store not available during testing.')
def test_fitbit_auth_get(test_client, init_database, client_auth_header):
    """
    GIVEN an API end point for Fitbit OAuth authentication
    WHEN the '/wearables/fitbit/auth/<user_id>' resource is requested (GET)
    THEN check the response is valid
    """

    response = test_client.get(
        '/wearables/fitbit/auth/1/',
        headers=client_auth_header
    )

    assert response.status_code == 200
    assert response.json['url']
    assert response.json['state']
    assert response.json['client_id']
    assert response.json['scope']
    assert response.json['response_type'] == 'code'
    assert response.json['redirect_uri'] == 'replace-this'

    data = Wearables.query.filter_by(user_id=1).first()

    assert data.state == response.json['state']

@pytest.mark.skip('AWS Parameter Store not available during testing.')
def test_fitbit_auth_post(test_client, init_database, client_auth_header):
    """
    GIVEN an API end point for Fitbit OAuth authentication
    WHEN the '/wearables/fitbit/auth/<user_id>' resource is requested (POST)
    THEN check the response is valid
    """
    # TODO: find a way to capture connection to fitbit,
    # and create a response for the grant code exchange.
    pass

def test_fitbit_auth_delete(test_client, init_database, client_auth_header):
    """
    GIVEN an API end point for Fitbit OAuth authentication
    WHEN the '/wearables/fitbit/auth/<user_id>' resource is requested (DELETE)
    THEN check the response is valid
    """

    response = test_client.delete(
        '/wearables/fitbit/auth/1/',
        headers=client_auth_header
    )

    assert response.status_code == 204

    data = Wearables.query.filter_by(user_id=1).first()

    assert data
    assert data.has_fitbit
    assert not data.registered_fitbit
