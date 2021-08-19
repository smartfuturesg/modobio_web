from odyssey.api.user.models import User, UserLogin

def test_get_client_storage_tiers(test_client):
    response = test_client.get(
        f'/client/datastoragetiers/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    # some simple checks for validity
    assert response.status_code == 200
    total_bytes = 0
    for item in response.json['items']:
        total_bytes += item['stored_bytes']
    assert total_bytes == response.json['total_stored_bytes']
