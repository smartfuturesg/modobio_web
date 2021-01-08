from flask.json import dumps

def test_get_lookup_races(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for lookup table goals
    WHEN the '/lookup/drinks/' resource  is requested (GET)
    THEN check the response is valid
    """
    # send get request for drinks lookup table
    response = test_client.get('/lookup/races/',
                                headers=client_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200