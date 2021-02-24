from flask.json import dumps

def test_get_telehealth_session_cost(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for lookup telehealth session cost
    WHEN the '/business/session-cost/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/lookup/business/session-cost/',
                                headers=client_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200
    assert response.json['items'][0]['session_min_cost'] == 50.00
    assert response.json['items'][0]['session_max_cost'] == 200.00    
    assert response.json['items'][0]['profession_type'] == 'Medical Doctor'
    assert response.json['items'][0]['territory'] == 'USA'
    assert response.json['items'][-1]['session_min_cost'] == 50.00
    assert response.json['items'][-1]['session_max_cost'] == 200.00    
    assert response.json['items'][-1]['profession_type'] == 'Medical Doctor'
    assert response.json['items'][-1]['territory'] == 'UK'