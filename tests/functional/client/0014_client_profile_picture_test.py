from flask.json import dumps
import pathlib
from odyssey import db

from odyssey.api.client.models import ClientInfo
from odyssey.api.user.models import User
from tests.functional.client.data import client_profile_picture_data


def test_put_client_profile_picture(test_client, init_database, staff_auth_header, client_auth_header):
    """
    GIVEN a api end point for adding and editing client profile picture
    WHEN the '/client/profile-picture/<client id>' resource  is requested to be changed (PUT)
    THEN check the response is valid
    """

    # Test a staff member trying to add client profile picture
    # Will return 401 unnauthorized
    response = test_client.put('/client/profile-picture/1/', 
                                headers=staff_auth_header, 
                                data=client_profile_picture_data)
    assert response.status_code == 401

    # Test client adding profile picture
    response = test_client.put('/client/profile-picture/1/', 
                                headers=client_auth_header, 
                                data=client_profile_picture_data)
    assert response.status_code == 200

    # Test client sending empty request
    response = test_client.put('/client/profile-picture/1/', 
                                headers=client_auth_header)
    assert response.status_code == 422


def test_delete_client_profile_picture(test_client, init_database, staff_auth_header, client_auth_header):
    """
    GIVEN a api end point for deleting client profile picture
    WHEN the '/client/profile-picture/<client id>' resource  is requested to be changed (DELETE)
    THEN check the response is valid
    """
    # Test a staff member trying to delete client profile picture
    # Will return 401 unnauthorized
    response = test_client.delete('/client/profile-picture/1/', 
                                headers=staff_auth_header)
    assert response.status_code == 401
    
    # Test client deleting profile picture
    response = test_client.delete('/client/profile-picture/1/', 
                                headers=client_auth_header)
    assert response.status_code == 204
