from flask.json import dumps

def test_get_professional_confirmation_window(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for lookup professional confirmation window
    WHEN the '/business/session-duration/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/lookup/business/professional-confirmation-window/',
                                headers=client_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200
    assert response.json['total_items'] == 47
    assert response.json['items'][0]['confirmation_window'] == 1
    assert response.json['items'][-1]['confirmation_window'] == 24