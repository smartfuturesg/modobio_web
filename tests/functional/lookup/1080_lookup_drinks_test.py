from flask.json import dumps

def test_get_lookup_drinks(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for lookup table goals
    WHEN the '/lookup/drinks/' resource  is requested (GET)
    THEN check the response is valid
    """
    # send get request for drinks lookup table
    response = test_client.get('/lookup/drinks/',
                                headers=client_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200

def test_get_lookup_drink_ingredients(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for lookup table drink ingredients
    WHEN the '/lookup/goals/<int:drink_id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    # send get request for drink ingredients on drink_id=1
    response = test_client.get('/lookup/drinks/ingredients/1/',
                                headers=client_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200