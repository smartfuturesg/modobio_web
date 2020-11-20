import datetime
import pathlib
import time

from flask.json import dumps
from requests.auth import _basic_auth_str

from odyssey.api.user.models import User, UserLogin
from werkzeug.security import check_password_hash
from .data import users_staff_passwords_data


def test_password_recovery_link(test_client, init_database):
    """
    GIVEN a api end point for creating a link for recovering passwords 
    WHEN the '/staff/password/forgot-password/recovery-link' resource  
    is requested to be created
    THEN check the response is valid
    """
    # Get staff member to reset lost password
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
 
    payload = {"email": staff.email}

    response = test_client.post('/staff/password/forgot-password/recovery-link/',
                                data=dumps(payload), 
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 200
    assert response.get_json()["token"]

def test_full_password_recovery_routine(test_client, init_database):
    """
    GIVEN a api end points for facilitating password recovery
    WHEN the '/staff/password/forgot-password/recovery-link' resource  
    is requested to be created, a token is returned. 
    This token can be used to change the password by sending a PUT
    request to `staff/password/forgot-password/reset`
    THEN check the response is valid
    """
    # Get staff member to reset lost password
    staff = User.query.filter_by(is_staff=True).first()
    
    payload_email = {"email": staff.email}

    response = test_client.post('/staff/password/forgot-password/recovery-link/',
                                data=dumps(payload_email), 
                                content_type='application/json')
    ##
    # Using the password reset token returned from the request above
    # send put request to reset password with new password in payload
    ##
    pswd_rest_token = response.get_json()["token"]

    payload_password_reset = {"password": users_staff_passwords_data["password"]}

    response = test_client.put(f'/staff/password/forgot-password/reset?reset_token={pswd_rest_token}',
                                data=dumps(payload_password_reset), 
                                content_type='application/json')
    # re-query database for staff member
    staff = User.query.filter_by(email=staff.email).first()

    assert response.status_code == 200

    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    assert staffLogin.check_password(password=payload_password_reset['password'])

def test_password_update(test_client, init_database):
    """
    GIVEN a api end point for creating a link for recovering passwords 
    WHEN the '/staff/password/update' PUT resource is requested
    THEN check the response is valid
    """
    # Get staff member to update password
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}
    ###
    # Update Password with the correct current password and a 
    # valid new password
    ###
    payload = {"current_password": users_staff_passwords_data["password"],
                "new_password": users_staff_passwords_data["new_password"]
    }

    response = test_client.post('/staff/password/update/',
                                headers=headers,
                                data=dumps(payload), 
                                content_type='application/json')
    # bring up staff member again for updated data
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).first()

    assert response.status_code == 200
    assert staffLogin.check_password(password=users_staff_passwords_data['new_password'])

    ###
    # Update Password with the incorrect current password and a 
    # valid new password
    ###

    response = test_client.post('/staff/password/update/',
                                headers=headers,
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 401