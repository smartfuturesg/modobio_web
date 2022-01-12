def test_get_blood_tests(test_client):
    response = test_client.get(
        '/lookup/bloodtests/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200

    response = test_client.get(
        '/lookup/bloodtests/ranges/CMP001/',
        headers=test_client.client_auth_header,
        content_type='application/json')
    
    assert response.status_code == 200