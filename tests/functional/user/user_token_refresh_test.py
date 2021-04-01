
from odyssey.api.user.models import User, UserLogin

from tests.functional.user.data import users_client_new_creation_data, users_staff_member_data


def test_staff_token_refresh(test_client, init_database):
    """
    GIVEN a api end point for retrieving API access and refresh tokens
    WHEN the '/user/token/refresh' resource  is requested to be created (POST)
    THEN check the response is valid
    """
    
    user = User.query.filter_by(email=users_staff_member_data['email']).one_or_none()
    user_login_details = UserLogin.query.filter_by(user_id=user.user_id).one_or_none()
    refresh_token = user_login_details.refresh_token
    # send post request for creating a new set of access tokens
    response = test_client.post(f'/user/token/refresh?refresh_token={refresh_token}',
                                content_type='application/json')

    

    assert response.status_code == 201

    # try agian with the same refresh token. It should now be revoked
    # send post request for creating a new set of access tokens
    response = test_client.post(f'/user/token/refresh?refresh_token={refresh_token}',
                                content_type='application/json')

    assert response.status_code == 401

def test_client_token_refresh(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for retrieving API access and refresh tokens
    WHEN the '/user/token/refresh' resource  is requested to be created (POST)
    THEN check the response is valid
    """
    
    user = User.query.filter_by(email=users_client_new_creation_data['email']).one_or_none()
    user_login_details = UserLogin.query.filter_by(user_id=user.user_id).one_or_none()

    refresh_token = user_login_details.refresh_token

    # send post request for creating a new set of access tokens
    response = test_client.post(f'/user/token/refresh?refresh_token={refresh_token}',
                                content_type='application/json')

    

    assert response.status_code == 201

    # try agian with the same refresh token. It should now be revoked
    # send post request for creating a new set of access tokens
    response = test_client.post(f'/user/token/refresh?refresh_token={refresh_token}',
                                content_type='application/json')

    assert response.status_code == 401
