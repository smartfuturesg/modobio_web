import pytest

from flask.json import dumps

from odyssey.api.user.models import UserSubscriptions

from .data import users_subscription_data

@pytest.fixture(scope='module', autouse=True)
def add_subscription(test_client):
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

    print(response.json)
    assert response.status_code == 201
    assert response.json['subscription_status'] == 'subscribed'

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

    assert response.status_code == 404

def test_get_subscription_history(test_client):
    response = test_client.get(
        f'/user/subscription/history/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
