from flask.json import dumps

def test_get_subscription_types(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for lookup subscription types
    WHEN the '/subscriptions/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/lookup/subscriptions/',
                                headers=client_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200
    assert response.json['items'][0]['name'] == "Team Member"
    assert response.json['items'][1]['cost'] == 9.99