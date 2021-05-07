from flask.json import dumps

from .data import device_token

# XXX: disable for now
import pytest
pytest.skip('Disabled for now', allow_module_level=True)

def test_device_registration_post(test_client, init_database, client_auth_header):
        """
        GIVEN an API endpoint for creating notifications,
        WHEN the POST /notifications/<user_id>/ resource is requested,
        THEN check that the response is valid.
        """

        response = test_client.post(
            '/notifications/push/register/1/',
            headers=client_auth_header,
            data=dumps(device_token),
            content_type='application/json')

        assert response.status_code == 201

        # POSTing the same device_id twice should not fail.
        response = test_client.post(
            '/notifications/push/register/1/',
            headers=client_auth_header,
            data=dumps(device_token),
            content_type='application/json')

        assert response.status_code == 201

def test_device_registration_get(test_client, init_database, client_auth_header):
        """
        GIVEN an API endpoint for retrieving notifications,
        WHEN the GET /notifications/<user_id>/ resource is requested,
        THEN check that the response is valid.
        """

        response = test_client.get(
            '/notifications/push/register/1/',
            headers=client_auth_header)

        assert response.status_code == 200
        assert type(response.json) == list
        assert len(response.json) == 2

def test_device_registration_delete(test_client, init_database, client_auth_header):
        """
        GIVEN an API endpoint for updating notifications,
        WHEN the PUT /notifications/<user_id>/<notification_id>/ resource is requested,
        THEN check that the response is valid.
        """
        d = {'device_token': device_token['device_token']}

        response = test_client.delete(
            '/notifications/push/register/1/',
            headers=client_auth_header,
            data=dumps(d),
            content_type='application/json')

        assert response.status_code == 204

        # Repeated delete should not fail
        response = test_client.delete(
            '/notifications/push/register/1/',
            headers=client_auth_header,
            data=dumps(d),
            content_type='application/json')

        assert response.status_code == 204

        # No output from DELETE, check again.
        response = test_client.get(
            '/notifications/push/register/1/',
            headers=client_auth_header)

        assert response.status_code == 200
        assert type(response.json) == list
        assert len(response.json) == 0
        assert response.json == []
