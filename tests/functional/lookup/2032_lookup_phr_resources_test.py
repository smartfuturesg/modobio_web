

def test_get_phr_resources(test_client):
    response = test_client.get(
        '/lookup/team/phr-resources/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200