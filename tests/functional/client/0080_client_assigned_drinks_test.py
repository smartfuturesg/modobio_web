import pytest
from flask.json import dumps

# from tests.functional.client.data import clients_assigned_drinks


@pytest.mark.skip(reason="deprecated, will be removed entirely in later release version")
def test_post_client_assigned_drink(test_client):
    response = test_client.post(
        f'/client/drinks/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(clients_assigned_drinks),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json.get('drink_id') == clients_assigned_drinks['drink_id']

    #test request when drink id does not exist
    clients_assigned_drinks['drink_id'] = 999999999

    response = test_client.post(
        f'/client/drinks/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(clients_assigned_drinks),
        content_type='application/json')

    assert response.status_code == 400


@pytest.mark.skip(reason="deprecated, will be removed entirely in later release version")
def test_get_client_assigned_drinks(test_client):
    response = test_client.get(
        f'/client/drinks/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200


@pytest.mark.skip(reason="deprecated, will be removed entirely in later release version")
def test_delete_client_assigned_drink(test_client):
    response = test_client.delete(
        f'/client/drinks/{test_client.client_id}/',
        data=dumps({'drink_ids': [1] }),
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
