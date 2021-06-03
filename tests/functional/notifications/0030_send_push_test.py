import pytest

from flask.json import dumps

from .data import device, alert, voip

@pytest.fixture(scope='session')
def register_device(test_client, init_database, client_auth_header):
    """ Register a debug device for push notifications. """

    device['device_platform'] = 'debug'

    response = test_client.post(
        '/notifications/push/register/1/',
        headers=client_auth_header,
        data=dumps(device),
        content_type='application/json')

    yield

    d = {'device_token': device['device_token']}

    response = test_client.delete(
        '/notifications/push/register/1/',
        headers=client_auth_header,
        data=dumps(d),
        content_type='application/json')

def test_send_alert(test_client, init_database, client_auth_header, register_device):
        """
        GIVEN an API endpoint for sending notifications,
        WHEN the POST /notifications/push/test/alert/<user_id>/ resource is requested,
        THEN check that the response is valid.
        """
        response = test_client.post(
            '/notifications/push/test/alert/1/',
            headers=client_auth_header,
            data=dumps(alert),
            content_type='application/json')

        assert response.status_code == 201
        assert response.json == {'message': alert['content']}

def test_send_voip(test_client, init_database, client_auth_header, register_device):
        """
        GIVEN an API endpoint for sending notifications,
        WHEN the POST /notifications/push/test/voip/<user_id>/ resource is requested,
        THEN check that the response is valid.
        """
        response = test_client.post(
            '/notifications/push/test/voip/1/',
            headers=client_auth_header,
            data=dumps(voip),
            content_type='application/json')

        assert response.status_code == 201
        assert response.json == {'message': voip['content']}
