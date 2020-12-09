from flask.json import dumps

from .data import users_subscription_data


def test_get_user_subscription(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for user subscription (GET)
    WHEN the '/user/subscription/' resource is requested
    THEN check the response is valid
    """

    #test GET method on client user_id = 1
    response = test_client.get('/user/subscription/1/',
                                headers=staff_auth_header,
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 200

def test_put_user_subscription(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end points for user subscriptions
    WHEN the '/user/subscription/' resource is requested (PUT) 
    THEN check the user's active subscription is udpated
    """

    response = test_client.put('/user/subscription/1/',
                                headers=staff_auth_header,
                                data=dumps(users_subscription_data), 
                                content_type='application/json')

    assert response.status_code == 200
    assert response.get_json()['subscription_type'] == 'subscribed'

    #test method with invalid subscription_type
    users_subscription_data['subscription_type'] = 'invalid_sub_type'

    response = test_client.put('/user/subscription/1/',
                                data=dumps(users_subscription_data), 
                                content_type='application/json')

    assert response.status_code == 400

    #test method with is_staff=True on an account that is not staff
    users_subscription_data['subscription_type'] = 'subscribed'
    users_subscription_data['is_staff'] = True

    response = test_client.put('/user/subscription/1/',
                                data=dumps(users_subscription_data), 
                                content_type='application/json')

    assert response.status_code == 404    

def test_get_subscription_history(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for user subscription history
    WHEN the '/user/subscription/history/' GET resource is requested
    THEN check the response is valid
    """

    #test GET method on client user_id = 1
    response = test_client.get('/user/subscription/history/1/',
                                headers=staff_auth_header,
                                content_type='application/json')

    assert response.status_code == 200