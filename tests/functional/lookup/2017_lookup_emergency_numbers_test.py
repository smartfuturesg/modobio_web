from flask.json import dumps

def test_get_emergency_numbers(test_client, init_database, client_auth_header):
    """
    GIVEN an api end point for lookup emergency phone numbers
    WHEN the '/lookup/emergency-numbers/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/lookup/emergency-numbers/',
                                headers=client_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200
    assert response.json['total_items'] == 81
