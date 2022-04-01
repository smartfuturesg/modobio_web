def test_get_lookup_dev_names(test_client):
    response = test_client.get(
    '/lookup/developers/',
    headers=test_client.client_auth_header,
    content_type='application/json')

    assert response.status_code == 200
    assert response.json['total_items'] == len(response.json['items'])