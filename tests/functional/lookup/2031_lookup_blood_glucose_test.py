def test_get_blood_tests(test_client):
    response = test_client.get(
        '/lookup/blood-glucose/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['total_items'] == 2