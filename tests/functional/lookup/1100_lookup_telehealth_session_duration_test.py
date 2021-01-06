from flask.json import dumps

def test_get_telehealth_session_duration(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for lookup telehealth session durations
    WHEN the '/business/session-duration/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/lookup/business/session-duration/',
                                headers=client_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200
    assert response.json['total_items'] == 11
    assert response.json['items'][0]['session_duration'] == 10
    assert response.json['items'][-1]['session_duration'] == 60