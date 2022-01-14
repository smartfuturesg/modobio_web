import base64
from datetime import datetime
from json import dump

from flask.json import dumps
from sqlalchemy import select

from odyssey.api.user.models import User, UserLogin, UserPendingEmailVerifications, UserTokenHistory
from tests.functional.user.data import users_new_self_registered_client_data

def test_client_user_email_update(test_client):
    """
    Update user's email from the client perspective
    """
    original_email = test_client.client.email

    response = test_client.patch(
        f'/user/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps({'email': 'test_email@gmail.com'}),
        content_type='application/json')

    user_pending_verification = UserPendingEmailVerifications.query.filter_by(user_id=test_client.client_id).first()
    breakpoint()
    assert response.status_code == 200
    # assert user.email == users_new_self_registered_client_data['email']
    # assert response.json['user_info']['modobio_id'] == None # email has not been verified
    # assert response.json['token']
    # assert response.json['refresh_token']
    # assert user.membersince == None
    # assert response.json['user_info']['email_verified'] == False


    # # Register the client's email address (token)
    # verification = UserPendingEmailVerifications.query.filter_by(user_id=user.user_id).one_or_none()
    # token = verification.token

    # response = test_client.get(f'/user/email-verification/token/{token}/')
    # assert response.status_code == 200

    # # Refresh user and ensure email is now verified
    # test_client.db.session.refresh(user)
    # assert user.email_verified == True
    # assert user.membersince
    # assert user.modobio_id

    
    # assert response.status_code == 401
    # assert token_history[0][0].event == 'login'
    # assert token_history[0][0].refresh_token == None

