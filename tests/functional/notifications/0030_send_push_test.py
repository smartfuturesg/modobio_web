import pytest

from flask.json import dumps

from .data import device, alert, voip
from tests.functional.staff.data import staff_profile_data

@pytest.fixture(scope='module')
def register_device(test_client):
    """ Register a debug device for push notifications. """

    device['device_platform'] = 'debug'

    response = test_client.post(
        f'/notifications/push/register/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(device),
        content_type='application/json')

    yield

    # Clean up
    token = {'device_token': device['device_token']}

    response = test_client.delete(
        f'/notifications/push/register/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(token),
        content_type='application/json')

def test_send_alert(test_client, register_device):
    response = test_client.post(
        f'/notifications/push/test/alert/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(alert),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json == {'message': alert['content']}

def test_send_voip(test_client, register_device):
    voip['content']['data']['staff_id'] = test_client.staff_id

    # Test when the staff memeber doesn't have a profile picture
    response = test_client.post(
        f'/notifications/push/test/voip/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(voip),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json == {'message': voip['content']}

    # Add staff profile information to test image
    test_client.put(
        f'/staff/profile/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=staff_profile_data['change_everything'])

    # Test when the staff member has a profile picture
    response = test_client.post(
        f'/notifications/push/test/voip/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(voip),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['message']['data']['staff_profile_picture']
    voip['content']['data']['staff_profile_picture'] = response.json['message']['data']['staff_profile_picture']
    assert response.json == {'message': voip['content']}
