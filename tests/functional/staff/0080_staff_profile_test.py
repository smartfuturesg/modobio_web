import base64

from flask import current_app
from requests.auth import _basic_auth_str

from odyssey.api.staff.models import StaffProfile

from .data import staff_profile_data

def test_get_staff_profile(test_client, init_database, staff_auth_header):
    """
    GIVEN an api end point for viewing a staff's profile
    WHEN the '/staff/profile/' resource is requested (GET)
    THEN check that the response is valid
    """

    response = test_client.get('/staff/profile/2/',
                                headers=staff_auth_header)
    
    # some simple checks for validity
    assert response.status_code == 200

def test_put_staff_profile(test_client, init_database, staff_auth_header):
    """
    GIVEN an api end point for updating a staff's profile
    WHEN the '/staff/profile/' resource is requested (PUT)
    THEN check that the profile is updated and the response is valid
    """

    response = test_client.put('/staff/profile/2/',
                                headers=staff_auth_header,
                                data=staff_profile_data['change_everything'])
    
    # some simple checks for validity
    assert response.status_code == 200
    assert response.json['firstname'] == 'Mario'
    assert response.json['middlename'] == 'The'
    assert response.json['lastname'] == 'Plumber'
    assert response.json['biological_sex_male'] == True
    assert response.json['bio'] == 'It\'s a me, Mario!'
    if not current_app.config['LOCAL_CONFIG']:
        assert response.json['profile_picture'] != None
    
    #get profile and ensure fields have been updated
    response = test_client.get('/staff/profile/2/',
                            headers=staff_auth_header)

    assert response.status_code == 200
    assert response.json['firstname'] == 'Mario'
    assert response.json['middlename'] == 'The'
    assert response.json['lastname'] == 'Plumber'
    assert response.json['biological_sex_male'] == True
    assert response.json['bio'] == 'It\'s a me, Mario!'
    if not current_app.config['LOCAL_CONFIG']:
        assert response.json['profile_picture'] != None

    #test changing only the picture
    response = test_client.put('/staff/profile/2/',
                                headers=staff_auth_header,
                                data=staff_profile_data['change_only_picture'])

    #if app is in local mode, s3 can't be accessed and response will succeed, but have no body
    if not current_app.config['LOCAL_CONFIG']:
        assert response.json['profile_picture'] != None
        assert response.status_code == 200
    else:
        assert response.status_code == 204
    
    response = test_client.get('/staff/profile/2/',
                            headers=staff_auth_header)

    assert response.status_code == 200
    if not current_app.config['LOCAL_CONFIG']:
        assert response.json['profile_picture'] != None

    #test deleting profile picture
    response = test_client.put('/staff/profile/2/',
                            headers=staff_auth_header,
                            data=staff_profile_data['remove_picture'])

    #just deleting the profile picture will succeed, but the response will have no body (even in local)
    assert response.status_code == 204

    #get profile and ensure picture has been removed
    response = test_client.get('/staff/profile/2/',
                            headers=staff_auth_header)
    assert response.status_code == 200
    if not current_app.config['LOCAL_CONFIG']:
        assert response.json['profile_picture'] == None