from flask.json import dumps

from .data import device_id1, device_id2

def test_device_registration_post(test_client, init_database, client_auth_header):
        """
        GIVEN an API endpoint for creating notifications,
        WHEN the POST /notifications/<user_id>/ resource is requested,
        THEN check that the response is valid.
        """

        response = test_client.post(
            '/notifications/push/register/1/',
            headers=client_auth_header,
            data=dumps(device_id1),
            content_type='application/json')

        assert response.status_code == 201

        response = test_client.post(
            '/notifications/push/register/1/',
            headers=client_auth_header,
            data=dumps(device_id2),
            content_type='application/json')

        assert response.status_code == 201

        # POSTing the same device_id twice should not fail.
        response = test_client.post(
            '/notifications/push/register/1/',
            headers=client_auth_header,
            data=dumps(device_id2),
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
        assert response.json == [device_id1, device_id2]

def test_device_registration_delete(test_client, init_database, client_auth_header):
        """
        GIVEN an API endpoint for updating notifications,
        WHEN the PUT /notifications/<user_id>/<notification_id>/ resource is requested,
        THEN check that the response is valid.
        """

        response = test_client.delete(
            '/notifications/push/register/1/',
            headers=client_auth_header,
            data=dumps(device_id2),
            content_type='application/json')

        assert response.status_code == 204

        # Repeated delete should not fail
        response = test_client.delete(
            '/notifications/push/register/1/',
            headers=client_auth_header,
            data=dumps(device_id2),
            content_type='application/json')

        assert response.status_code == 204

        # No output from DELETE, check again.
        response = test_client.get(
            '/notifications/push/register/1/',
            headers=client_auth_header)

        assert response.status_code == 200
        assert type(response.json) == list
        assert len(response.json) == 1
        assert response.json == [device_id1]
