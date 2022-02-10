import pytest

from flask.json import dumps

from odyssey.api.user.models import UserSubscriptions

from .data import users_subscription_data

# Main test user client@modobio.com already has a subscription,
# per database/0003_seed_users.sql
# If that changes at any point, request the below fixture in any of the tests.

@pytest.fixture(scope='module')
def subscription(test_client):
    sub = UserSubscriptions(
        user_id=test_client.client_id,
        is_staff=False,
        subscription_status='unsubscribed',
        subscription_type_id=1)

    test_client.db.session.add(sub)
    test_client.db.session.commit()

def test_get_user_subscription(test_client):
    response = test_client.get(
        f'/user/subscription/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')
        
    # some simple checks for validity
    assert response.status_code == 200

def test_put_user_subscription(test_client):
    response = test_client.put(
        f'/user/subscription/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(users_subscription_data),
        content_type='application/json')

    # The transaction_id being used will be moving from valid to invalid as we test this feature
    # 201 means the requested transaction_id is active on the applestore. 
    # 400 indicates the transaction_is is tied to an inactive subscription and
    #   cannot be used to start a new subcription on the modobio end. 
    assert response.status_code in (201, 400)
    assert response.json['subscription_status'] in ('subscribed', 'unsubscribed')

    #test method with invalid subscription_type
    users_subscription_data['subscription_type_id'] = 9999

    response = test_client.put(
        f'/user/subscription/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(users_subscription_data),
        content_type='application/json')

    assert response.status_code == 400

    #test method with is_staff=True on an account that is not staff
    users_subscription_data['subscription_type_id'] = 2
    users_subscription_data['is_staff'] = True

    response = test_client.put(
        f'/user/subscription/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(users_subscription_data),
        content_type='application/json')

    assert response.status_code == 401

def test_get_subscription_history(test_client):
    response = test_client.get(
        f'/user/subscription/history/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
