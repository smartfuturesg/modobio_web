from werkzeug.security import check_password_hash

from flask.json import dumps
from sqlalchemy import select

from odyssey.api.user.models import User, UserLogin
from .data import users_staff_passwords_data

def test_password_recovery_link(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for creating a link for recovering passwords 
    WHEN the '/user/password/forgot-password/recovery-link' resource  
    is requested to be created
    THEN check the response is valid
    """
    # use a random client member
    client = User.query.filter_by(is_client=True).first()
    payload = {"email": client.email}

    response = test_client.post('/user/password/forgot-password/recovery-link/',
                                data=dumps(payload), 
                                content_type='application/json')
    # some simple checks for validity
    assert response.status_code == 200
    assert response.get_json()["token"]

def test_full_password_recovery_routine(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end points for facilitating password recovery
    WHEN the '/staff/password/forgot-password/recovery-link' resource  
    is requested to be created, a token is returned. 
    This token can be used to change the password by sending a PUT
    request to `staff/password/forgot-password/reset`
    THEN check the response is valid
    """
    # user details for password recovery throughout these tests
    global password_recovery_user, password_recovery_user_login

    password_recovery_user, password_recovery_user_login = init_database.session.execute(
        select(User, UserLogin).
        join(UserLogin, User.user_id == UserLogin.user_id).
        where(User.user_id == 2)
    ).one_or_none()

    # Get user member to reset lost password
    payload_email = {"email": password_recovery_user.email}

    response = test_client.post('/user/password/forgot-password/recovery-link/',
                                data=dumps(payload_email), 
                                content_type='application/json')
    ##
    # Using the password reset token returned from the request above
    # send put request to reset password with new password in payload
    ##
    pswd_rest_token = response.get_json()["token"]

    payload_password_reset = {"password": users_staff_passwords_data["password"]}

    response = test_client.put(f'/user/password/forgot-password/reset?reset_token={pswd_rest_token}',
                                data=dumps(payload_password_reset), 
                                content_type='application/json')

    init_database.session.refresh(password_recovery_user_login)
    
    assert response.status_code == 200
    assert check_password_hash(password_recovery_user_login.password, payload_password_reset['password'])

def test_password_update(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for creating a link for recovering passwords 
    WHEN the '/user/password/update' PUT resource is requested
    THEN check the response is valid
    """
    ###
    # Update Password with the correct current password and a 
    # valid new password
    ###
    payload = {"current_password": users_staff_passwords_data["password"],
                "new_password": users_staff_passwords_data["new_password"]
    }

    response = test_client.post('/user/password/update/',
                                headers=staff_auth_header,
                                data=dumps(payload), 
                                content_type='application/json')

    init_database.session.refresh(password_recovery_user_login)
    
    assert response.status_code == 200
    assert check_password_hash(password_recovery_user_login.password, users_staff_passwords_data['new_password'])

    ###
    # Update Password with the incorrect current password and a 
    # valid new password
    ###

    response = test_client.post('/user/password/update/',
                                headers=staff_auth_header,
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 401