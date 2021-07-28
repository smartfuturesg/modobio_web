from flask.json import dumps

def test_get_subscription_types(test_client):
    response = test_client.get(
        '/lookup/subscriptions/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['items'][0]['name'] == "Team Member"
    assert response.json['items'][1]['cost'] == 9.99
