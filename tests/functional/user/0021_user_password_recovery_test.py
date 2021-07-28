from werkzeug.security import check_password_hash

from flask.json import dumps
from sqlalchemy import select

from odyssey.api.user.models import User, UserLogin
from .data import users_staff_passwords_data

def test_password_recovery_link(test_client):
    response = test_client.post(
        '/user/password/forgot-password/recovery-link/',
        data=dumps({'email': test_client.client_email}),
        content_type='application/json')

    # some simple checks for validity
    assert response.status_code == 200
    assert response.json['token']

def test_full_password_recovery_routine(test_client):
    user_login = (test_client.db.session.execute(
        select(UserLogin)
        .filter_by(user_id=test_client.staff_id))
        .one_or_none())[0]

    response = test_client.post(
        '/user/password/forgot-password/recovery-link/',
        data=dumps({'email': test_client.staff_email}),
        content_type='application/json')

    ##
    # Using the password reset token returned from the request above
    # send put request to reset password with new password in payload
    ##
    pswd_rest_token = response.json['token']
    payload_password_reset = {'password': users_staff_passwords_data['password']}

    response = test_client.put(
        f'/user/password/forgot-password/reset?reset_token={pswd_rest_token}',
        data=dumps(payload_password_reset),
        content_type='application/json')

    test_client.db.session.refresh(user_login)

    assert response.status_code == 200
    assert check_password_hash(user_login.password, payload_password_reset['password'])

def test_password_update(test_client):
    ###
    # Update Password with the correct current password and a
    # valid new password
    ###
    user_login = (test_client.db.session.execute(
        select(UserLogin)
        .filter_by(user_id=test_client.staff_id))
        .one_or_none())[0]

    payload = {
        'current_password': users_staff_passwords_data['password'],
        'new_password': users_staff_passwords_data['new_password']}

    response = test_client.post(
        '/user/password/update/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    test_client.db.session.refresh(user_login)

    assert response.status_code == 200
    assert check_password_hash(user_login.password, users_staff_passwords_data['new_password'])

    ###
    # Update Password with the incorrect current password and a
    # valid new password
    ###

    response = test_client.post(
        '/user/password/update/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 401
