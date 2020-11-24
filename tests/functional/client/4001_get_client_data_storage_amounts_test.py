from requests.auth import _basic_auth_str

from odyssey.api.user.models import User, UserLogin


def test_get_client_storage_tiers(test_client, init_database, staff_auth_header):
    """
    GIVEN a api endpoint for creating a new client at home registration
    WHEN the '/client/remoteregistration/new' resource  is requested to be creates (POST)
    THEN check the response is valid
    """    
    
    response = test_client.get('/client/datastoragetiers/',
                                headers=staff_auth_header, 
                                content_type='application/json')

    data = response.get_json()
    # some simple checks for validity
    assert response.status_code == 200
    total_bytes = 0
    for item in data['items']:
        total_bytes += item['stored_bytes']
    assert total_bytes == data['total_stored_bytes']