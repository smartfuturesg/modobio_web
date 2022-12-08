

def test_get_cred_types(test_client):
    response = test_client.get(
        '/lookup/credential-types/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['total_items'] == 4