from sqlalchemy import select
from sqlalchemy.sql.expression import desc

from odyssey.api.user.models import User, UserLogin, UserTokenHistory

from tests.functional.user.data import users_client_new_creation_data, users_staff_member_data


def test_staff_token_refresh(test_client, init_database):
    """
    GIVEN a api end point for retrieving API access and refresh tokens
    WHEN the '/user/token/refresh' resource  is requested to be created (POST)
    THEN check the response is valid
    """

    user = init_database.session.execute(
            select(User).
            where(User.email==users_staff_member_data['email'])
        ).one_or_none()[0]

    refresh_tokens_stmt = select(UserTokenHistory.refresh_token). \
            where(UserTokenHistory.user_id==user.user_id). \
            order_by(UserTokenHistory.created_at.desc())

    # bring up all refresh tokens so far
    refresh_tokens = init_database.session.execute(refresh_tokens_stmt).scalars().all()
        
    current_token_count = len(refresh_tokens)
    # send post request for creating a new set of access tokens
    response = test_client.post(f'/user/token/refresh?refresh_token={refresh_tokens[0]}',
                                content_type='application/json')

    # pull up refresh tokens again
    refresh_tokens = init_database.session.execute(refresh_tokens_stmt).scalars().all()
    assert response.status_code == 201
    assert len(refresh_tokens) - current_token_count == 1 

    # try agian with the same refresh token. It should now be revoked
    # send post request for creating a new set of access tokens
    response = test_client.post(f'/user/token/refresh?refresh_token={refresh_tokens[-1]}',
                                content_type='application/json')

    # pull up login attempts by this client a new failed attempt should be in the database
    token_history = init_database.session.execute(
            select(UserTokenHistory). \
            where(UserTokenHistory.user_id==user.user_id). \
            order_by(UserTokenHistory.created_at.desc())
        ).all()
        
    assert response.status_code == 401
    assert len(token_history) - current_token_count == 2

def test_client_token_refresh(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for retrieving API access and refresh tokens
    WHEN the '/user/token/refresh' resource  is requested to be created (POST)
    THEN check the response is valid
    """
    user = User.query.filter_by(email=users_client_new_creation_data['email']).one_or_none()

    refresh_tokens_stmt = select(UserTokenHistory.refresh_token). \
        where(UserTokenHistory.user_id==user.user_id). \
        order_by(UserTokenHistory.created_at.desc())

    # bring up all refresh tokens so far
    refresh_tokens = init_database.session.execute(refresh_tokens_stmt).scalars().all()
    current_token_count = len(refresh_tokens)        
    # send post request for creating a new set of access tokens
    response = test_client.post(f'/user/token/refresh?refresh_token={refresh_tokens[0]}',
                                content_type='application/json')


    # pull up refresh tokens again
    refresh_tokens = init_database.session.execute(refresh_tokens_stmt).scalars().all()
    assert response.status_code == 201
    assert len(refresh_tokens) - current_token_count == 1 

    # try agian with the same refresh token. It should now be revoked
    # send post request for creating a new set of access tokens
    response = test_client.post(f'/user/token/refresh?refresh_token={refresh_tokens[-1]}',
                                content_type='application/json')

    # pull up login attempts by this client a new failed attempt should be in the database
    token_history = init_database.session.execute(
            select(UserTokenHistory). \
            where(UserTokenHistory.user_id==user.user_id). \
            order_by(UserTokenHistory.created_at.desc())
        ).all()
        
    assert response.status_code == 401
    assert len(token_history) - current_token_count == 2
