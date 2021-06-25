from flask.json import dumps

def test_get_currencies(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for lookup currencies
    WHEN the '/lookup/currencies/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/lookup/currencies/',
                                headers=client_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200
    assert response.json['total_items'] == 1
    assert response.json['items'][0]['country'] == 'USA'