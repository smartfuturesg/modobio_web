

from requests.auth import _basic_auth_str

from odyssey.models.staff import Staff


def test_get_client_storage_tiers(test_client, init_database):
    """
    GIVEN a api endpoint for creating a new client at home registration
    WHEN the '/client/remoteregistration/new' resource  is requested to be creates (POST)
    THEN check the response is valid
    """

    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    response = test_client.get('/client/datastoragetiers/',
                                headers=headers, 
                                content_type='application/json')

    data = response.get_json()
    # some simple checks for validity
    assert response.status_code == 200
    assert data['items'][0]['stored_bytes'] == data['total_stored_bytes']

