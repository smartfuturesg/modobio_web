import base64
from datetime import datetime
from json import dump

from flask.json import dumps
from sqlalchemy import select

from odyssey.api.user.models import User, UserLogin, UserPendingEmailVerifications, UserTokenHistory

def test_client_user_email_update(test_client):
    """
    Update user's email from the client perspective

    use user/email-verification/code to verify email 
    """
    original_email = test_client.client.email
    new_email_payload = {'email': 'test_email_client_self@gmail.com'}
    response = test_client.patch(
        f'/user/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(new_email_payload),
        content_type='application/json')

    user_pending_verification = UserPendingEmailVerifications.query.filter_by(user_id=test_client.client_id).first()
    assert response.status_code == 200
    assert response.json['email_verification_code']
    assert user_pending_verification.email == new_email_payload['email']
    verification_code = response.json['email_verification_code']


    # Register the client's email address (code)

    response = test_client.post(f'/user/email-verification/code/{test_client.client_id}/?code={verification_code}')
    
    # # Refresh user and ensure email is updated
    test_client.db.session.refresh(test_client.client)
    assert response.status_code == 200
    assert test_client.client.email == new_email_payload['email']

    # return email to what it was previously
    test_client.client.email = original_email
    test_client.db.session.commit()

def test_staff_user_email_update(test_client):
    """
    Update user's email from the staff-self perspective. 
    This is mostly to ensure the auth system is working correctly.

    use user/email-verification/token to verify email 

    """
    original_email = test_client.staff.email
    new_email_payload = {'email': 'test_email_staff_self@gmail.com'}
    response = test_client.patch(
        f'/user/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(new_email_payload),
        content_type='application/json')

    user_pending_verification = UserPendingEmailVerifications.query.filter_by(user_id=test_client.staff_id).first()

    assert response.status_code == 200
    assert response.json['email_verification_code']
    assert user_pending_verification.email == new_email_payload['email']

    verification_token = user_pending_verification.token

    # Register the client's email address (token)

    response = test_client.get(f'/user/email-verification/token/{verification_token}/')
    
    # # Refresh user and ensure email is updated
    test_client.db.session.refresh(test_client.staff)
    assert response.status_code == 200
    assert test_client.staff.email == new_email_payload['email']

    # return email to what it was previously
    test_client.staff.email = original_email
    test_client.db.session.commit()

def test_client_services_user_email_update(test_client):
    """
    Update user's email from the client services perspective. CS roles should be allowed
    to update emails on behalf of users: https://atventurepartners.atlassian.net/browse/NRV-2756

    The test_client.staff user should have the cs role.
    
    This is mostly to ensure the auth system is working correctly.

    use user/email-verification/token to verify email 

    """
    original_email = test_client.client.email
    new_email_payload = {'email': 'test_email_client_self@gmail.com'}
    response = test_client.patch(
        f'/user/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(new_email_payload),
        content_type='application/json')

    user_pending_verification = UserPendingEmailVerifications.query.filter_by(user_id=test_client.client_id).first()
    assert response.status_code == 200
    assert response.json['email_verification_code']
    assert user_pending_verification.email == new_email_payload['email']
    verification_code = response.json['email_verification_code']


    # Register the client's email address (code)

    response = test_client.post(f'/user/email-verification/code/{test_client.client_id}/?code={verification_code}')
    
    # # Refresh user and ensure email is updated
    test_client.db.session.refresh(test_client.client)
    assert response.status_code == 200
    assert test_client.client.email == new_email_payload['email']

    # return email to what it was previously
    test_client.client.email = original_email
    test_client.db.session.commit()


