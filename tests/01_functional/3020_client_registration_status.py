

from odyssey.models.staff import Staff


def test_get_registration_statis(test_client, init_database):
    """
    GIVEN a api end point for strength assessment
    WHEN the '/trainer/assessment/strength/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on clientid = 1 
    response = test_client.get('/client/registrationstatus/1/',
                                headers=headers, 
                                content_type='application/json')

    assert response.status_code == 200

