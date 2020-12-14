from flask.json import dumps

def test_get_lookup_goals(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for lookup table goals
    WHEN the '/lookup/goals/' resource  is requested (GET)
    THEN check the response is valid
    """
    # send get request for client info on user_id = 1 
    response = test_client.get('/lookup/goals/',
                                headers=client_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200