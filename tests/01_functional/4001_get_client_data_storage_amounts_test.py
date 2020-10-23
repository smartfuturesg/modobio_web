from requests.auth import _basic_auth_str

from odyssey.models.user import User, UserLogin


def test_get_client_storage_tiers(test_client, init_database):
    """
    GIVEN a api endpoint for creating a new client at home registration
    WHEN the '/client/remoteregistration/new' resource  is requested to be creates (POST)
    THEN check the response is valid
    """

    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    response = test_client.get('/client/datastoragetiers/',
                                headers=headers, 
                                content_type='application/json')

    data = response.get_json()
    # some simple checks for validity
    assert response.status_code == 200
    total_bytes = 0
    for item in data['items']:
        total_bytes += item['stored_bytes']
    assert total_bytes == data['total_stored_bytes']