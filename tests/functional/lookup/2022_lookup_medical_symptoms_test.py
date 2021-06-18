from flask.json import dumps

def test_get_medical_symptoms(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for lookup medical symptoms
    WHEN the '/lookup/medical-symptoms/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/lookup/medical-symptoms/',
                                headers=client_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200
    assert response.json['total_items'] == 27
    assert response.json['items'][0]['name'] == 'Abdominal Pain'