import base64

from flask.json import dumps

from odyssey.api.user.models import User, UserPendingEmailVerifications
from odyssey.api.client.models import ClientInfo, ClientConsent
from tests.functional.client.data import client_info_put_test_data
from tests.functional.user.data import users_new_user_client_data

def test_get_client_info(test_client):
    response = test_client.get(
        f'/client/{test_client.client_id}/',
        headers=test_client.client_auth_header)

    assert response.status_code == 200
    assert response.json['user_info']['user_id'] == test_client.client_id
    assert response.json['user_info']['modobio_id']

def test_put_client_info(test_client):
    # Attempt to change user_id
    data = {'client_info': {'user_id': 10}}

    response = test_client.put(
        f'/client/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(data),
        content_type='application/json')

    assert response.status_code == 400

    # Attempt to change the guardian name.
    data = {'client_info': {'guardianname': 'Testy'}}

    response = test_client.put(
        f'/client/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(data),
        content_type='application/json')

    client = ClientInfo.query.filter_by(user_id=test_client.client_id).one_or_none()
    assert response.status_code == 200
    assert client.guardianname == 'Testy'

    # test full payload of updates to client info data
    response = test_client.put(
        f'/client/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(client_info_put_test_data),
        content_type='application/json')

    assert response.status_code == 200
    assert response.json["client_info"]["primary_goal"] == "('Recovery',)"
    assert response.json["client_info"]["primary_macro_goal"] == "('Gain the best understanding I can of my health at any point in time.',)"
    assert response.json["client_info"]["primary_goal_description"] == "To try out something new"

def test_creating_new_client(test_client):
    payload = users_new_user_client_data['user_info']

    # send post request for a new client user account
    response = test_client.post(
        '/user/client/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    user = User.query.filter_by(email=users_new_user_client_data['user_info']['email']).first()
    assert response.status_code == 201
    assert user.email == users_new_user_client_data['user_info']['email']
    assert response.json['user_info']['modobio_id']

    # Register the client's email address (token)
    verification = UserPendingEmailVerifications.query.filter_by(user_id=user.user_id).one_or_none()
    token = verification.token

    response = test_client.get(f'/user/email-verification/token/{token}/')
    assert response.status_code == 200

    ###############
    # Use generated password to test token generation
    # 1) correct password
    # 2) Incorrect password
    ###############
    password = payload['password']
    valid_credentials = base64.b64encode(
            f"{users_new_user_client_data['user_info']['email']}:{password}".encode("utf-8")).decode("utf-8")
    headers = {'Authorization': f'Basic {valid_credentials}'}

    response = test_client.post(
        '/client/token/',
        headers=headers,
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['email'] == users_new_user_client_data['user_info']['email']

    password = 'thewrongpassword?'
    valid_credentials = base64.b64encode(
            f"{users_new_user_client_data['user_info']['email']}:{password}".encode("utf-8")).decode("utf-8")
    headers = {'Authorization': f'Basic {valid_credentials}'}

    response = test_client.post(
        '/client/token/',
        headers=headers,
        content_type='application/json')

    assert response.status_code == 401
