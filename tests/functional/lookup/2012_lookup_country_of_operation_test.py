from flask.json import dumps

def test_get_countries_of_operation(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for lookup countries of operation
    WHEN the '/lookup/business/countries-of-operations/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/lookup/business/countries-of-operations/',
                                headers=client_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200
    assert response.json['total_items'] == 1
    assert response.json['items'][0]['country'] == 'United States (USA)'