import pytest

from flask.json import dumps

from odyssey.api.wearables.models import Wearables, WearablesFitbit

from .data import wearables_data

def test_fitbit_pre_auth(test_client):
    data = Wearables.query.filter_by(user_id=test_client.client_id).one_or_none()

    # Not checking the data, just differentiating between PUT or POST
    if data:
        op = test_client.put
    else:
        op = test_client.post

    response = op(
        f'/wearables/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(wearables_data),
        content_type='application/json')

    assert response.status_code in (201, 204)

    data = Wearables.query.filter_by(user_id=test_client.client_id).first()

    assert data
    assert data.has_fitbit
    assert not data.registered_fitbit

# @pytest.mark.skip('AWS Parameter Store not available during testing.')
def test_fitbit_auth_get(test_client):
    response = test_client.get(
        f'/wearables/fitbit/auth/{test_client.client_id}/',
        headers=test_client.client_auth_header)

    assert response.status_code == 200
    assert response.json['url']
    assert response.json['state']
    assert response.json['client_id']
    assert response.json['scope']
    assert response.json['response_type'] == 'code'
    assert response.json['redirect_uri'] == 'replace-this'

    data = WearablesFitbit.query.filter_by(user_id=test_client.client_id).first()

    assert data.oauth_state == response.json['state']

@pytest.mark.skip('AWS Parameter Store not available during testing.')
def test_fitbit_auth_post(test_client):
    # TODO: find a way to capture connection to fitbit,
    # and create a response for the grant code exchange.
    pass

def test_fitbit_auth_delete(test_client):
    response = test_client.delete(
        f'/wearables/fitbit/auth/{test_client.client_id}/',
        headers=test_client.client_auth_header)

    assert response.status_code == 204

    data = Wearables.query.filter_by(user_id=test_client.client_id).first()

    assert data
    assert data.has_fitbit
    assert not data.registered_fitbit
