def test_get_keys(test_client):
    response = test_client.get(
        '/lookup/keys/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200