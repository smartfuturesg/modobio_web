import pathlib

from flask.json import dumps

from odyssey.api.client.models import ClientInfo
from odyssey.api.user.models import User
from tests.functional.client.data import client_profile_picture_data


def test_put_client_profile_picture(test_client):

    # Test a staff member trying to add client profile picture
    # Will return 401 unnauthorized
    response = test_client.put(
        f'/client/profile-picture/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=client_profile_picture_data)
        
    assert response.status_code == 401

    # Test client adding profile picture
    response = test_client.put(
        f'/client/profile-picture/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=client_profile_picture_data)

    assert response.status_code == 200

    # Test client sending empty request
    response = test_client.put(
        f'/client/profile-picture/{test_client.client_id}/',
        headers=test_client.client_auth_header)

    assert response.status_code == 400

def test_delete_client_profile_picture(test_client):
    # Test a staff member trying to delete client profile picture
    # Will return 401 unnauthorized
    response = test_client.delete(
        f'/client/profile-picture/{test_client.client_id}/',
        headers=test_client.staff_auth_header)

    assert response.status_code == 401

    # Test client deleting profile picture
    response = test_client.delete(
        f'/client/profile-picture/{test_client.client_id}/',
        headers=test_client.client_auth_header)

    assert response.status_code == 204
