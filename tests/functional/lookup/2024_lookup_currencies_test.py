from flask.json import dumps

def test_get_currencies(test_client):
    response = test_client.get(
        '/lookup/currencies/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['total_items'] == 1
    assert response.json['items'][0]['country'] == 'USA'
