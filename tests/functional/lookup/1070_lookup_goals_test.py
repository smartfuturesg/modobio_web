from flask.json import dumps

def test_get_lookup_goals(test_client):
    response = test_client.get(
        '/lookup/goals/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200

def test_get_lookup_macro_goals(test_client):
    response = test_client.get(
        '/lookup/macro-goals/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
