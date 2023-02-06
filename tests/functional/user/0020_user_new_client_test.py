import base64

from flask.json import dumps
from sqlalchemy import select

from odyssey.api.user.models import User, UserPendingEmailVerifications, UserTokenHistory
from tests.functional.user.data import users_new_self_registered_client_data, users_bad_password_client_data


def test_self_registered_new_client(test_client):
    # We don't need a staff to be logged-in for a client to self-register
    payload = users_new_self_registered_client_data

    # send post request for a new client user account
    response = test_client.post(
        '/user/client/',
        data=dumps(payload),
        content_type='application/json')

    user = User.query.filter_by(email=payload['email']).first()

    assert response.status_code == 201
    assert user.email == users_new_self_registered_client_data['email']
    assert response.json['user_info']['modobio_id'] == None # email has not been verified
    assert response.json['token']
    assert response.json['refresh_token']
    assert user.membersince == None
    assert response.json['user_info']['email_verified'] == False

    # Register the client's email address (token)
    verification = UserPendingEmailVerifications.query.filter_by(user_id=user.user_id).one_or_none()
    token = verification.token

    response = test_client.get(f'/user/email-verification/token/{token}/')
    assert response.status_code == 200

    # Refresh user and ensure email is now verified
    test_client.db.session.refresh(user)
    assert user.email_verified == True
    assert user.membersince
    assert user.modobio_id

    ####
    #Test token generation and login history
    ####

    password = payload['password']
    valid_credentials = base64.b64encode(
            f"{users_new_self_registered_client_data['email']}:{password}".encode("utf-8")).decode("utf-8")

    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post(
        '/client/token/',
        headers=headers,
        content_type='application/json')

    # pull up login attempts by this client
    token_history = test_client.db.session.execute(
            select(UserTokenHistory). \
            where(UserTokenHistory.user_id==user.user_id). \
            order_by(UserTokenHistory.created_at.desc())
        ).all()

    assert response.status_code == 201
    assert response.json['email'] == users_new_self_registered_client_data['email']
    assert response.json['refresh_token'] == token_history[0][0].refresh_token
    assert token_history[0][0].event == 'login'

    #Test using wrong password
    password = 'thewrongpassword?'
    valid_credentials = base64.b64encode(
            f"{users_new_self_registered_client_data['email']}:{password}".encode("utf-8")).decode("utf-8")

    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post(
        '/client/token/',
        headers=headers,
        content_type='application/json')

    # pull up login attempts by this client. Ensure failed loginwas recorded
    token_history = test_client.db.session.execute(
            select(UserTokenHistory). \
            where(UserTokenHistory.user_id==user.user_id). \
            order_by(UserTokenHistory.created_at.desc())
        ).all()

    assert response.status_code == 401
    assert token_history[0][0].event == 'login'
    assert token_history[0][0].refresh_token == None

def test_blacklisted_email_address(test_client):
    payload = {
        'email': 'user@10-minute-mail.com',
        'password': 'password0987'}

    response = test_client.post(
        '/user/client/',
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 400
    assert response.json['message'] == 'Email adresses from "10-minute-mail.com" are not allowed.'

def test_update_blacklisted_email_address(test_client):
    payload = {'user_info': {'email': 'user@10-minute-mail.com'}}

    response = test_client.put(
        f'/client/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 400
    assert response.json['message'] == 'Email adresses from "10-minute-mail.com" are not allowed.'

def test_password_requirements(test_client):
    payload = users_bad_password_client_data

    # send post request for a new client user account
    response = test_client.post(
        '/user/client/',
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 400