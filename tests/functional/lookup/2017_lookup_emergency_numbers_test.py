from flask.json import dumps

def test_get_emergency_numbers(test_client):
    response = test_client.get(
        '/lookup/emergency-numbers/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['total_items'] == 81
