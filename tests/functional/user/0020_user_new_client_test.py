import base64
import pathlib
import time
from datetime import datetime

from flask.json import dumps
from requests.auth import _basic_auth_str

from odyssey.api.user.models import User, UserLogin, UserPendingEmailVerifications
from tests.functional.user.data import users_new_self_registered_client_data
from odyssey import db

def test_self_registered_new_client(test_client, init_database):
    """
    GIVEN a api end point for regitering a new user client
    WHEN the 'user/client/' resource  is requested 
    THEN check the response is valid
    """

    # We don't need a staff to be logged-in for a client to self-register
    payload = users_new_self_registered_client_data
    
    # send post request for a new client user account
    response = test_client.post('/user/client/', 
                                data=dumps(payload), 
                                content_type='application/json')

    user = User.query.filter_by(email=payload['email']).first()
    
    assert response.status_code == 201
    assert user.email == users_new_self_registered_client_data['email']
    assert response.json['user_info']['modobio_id']
    assert response.json['token']
    assert response.json['refresh_token']
    assert response.json['user_info']['email_verified'] == False

    # Register the client's email address (token)
    verification = UserPendingEmailVerifications.query.filter_by(user_id=user.user_id).one_or_none()
    token = verification.token

    response = test_client.post('/user/email-verification/token/' + token + '/')
    assert response.status_code == 200

    # Refresh user and ensure email is now verified
    db.session.refresh(user)
    assert user.email_verified == True

    #Test token generation
    password = payload['password']
    valid_credentials = base64.b64encode(
            f"{users_new_self_registered_client_data['email']}:{password}".encode("utf-8")).decode("utf-8")
    
    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post('/client/token/',
                            headers=headers, 
                            content_type='application/json')

    assert response.status_code == 201
    assert response.json['email'] == users_new_self_registered_client_data['email']


    #Test using wrong password
    password = 'thewrongpassword?'
    valid_credentials = base64.b64encode(
            f"{users_new_self_registered_client_data['email']}:{password}".encode("utf-8")).decode("utf-8")
    
    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post('/client/token/',
                            headers=headers, 
                            content_type='application/json')
    
    assert response.status_code == 401
