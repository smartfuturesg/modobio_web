from flask.json import dumps

from .data import device

def test_device_registration_post(test_client):
        response = test_client.post(
            f'/notifications/push/register/{test_client.client_id}/',
            headers=test_client.client_auth_header,
            data=dumps(device),
            content_type='application/json')

        assert response.status_code == 201

        # POSTing the same device_id twice should not fail.
        response = test_client.post(
            f'/notifications/push/register/{test_client.client_id}/',
            headers=test_client.client_auth_header,
            data=dumps(device),
            content_type='application/json')

        assert response.status_code == 201

def test_device_registration_get(test_client):
        response = test_client.get(
            f'/notifications/push/register/{test_client.client_id}/',
            headers=test_client.client_auth_header)

        assert response.status_code == 200
        assert type(response.json) == list
        
        assert len(response.json) == 1

def test_device_registration_delete(test_client):
        d = {'device_token': device['device_token']}

        response = test_client.delete(
            f'/notifications/push/register/{test_client.client_id}/',
            headers=test_client.client_auth_header,
            data=dumps(d),
            content_type='application/json')

        assert response.status_code == 204

        # Repeated delete should not fail
        response = test_client.delete(
            f'/notifications/push/register/{test_client.client_id}/',
            headers=test_client.client_auth_header,
            data=dumps(d),
            content_type='application/json')

        assert response.status_code == 204

        # No output from DELETE, check again.
        response = test_client.get(
            f'/notifications/push/register/{test_client.client_id}/',
            headers=test_client.client_auth_header)

        assert response.status_code == 200
        assert type(response.json) == list
        assert len(response.json) == 0
        assert response.json == []
