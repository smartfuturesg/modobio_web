from flask.json import dumps

def test_get_organizations(test_client):
    response = test_client.get(
        '/lookup/organizations/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['total_items'] == 3
    assert response.json['items'][0]['org_name'] == 'Wheel'
