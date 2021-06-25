from flask.json import dumps

def test_get_organizations(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for lookup organizations
    WHEN the '/lookup/organizations/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/lookup/organizations/',
                                headers=client_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200
    assert response.json['total_items'] == 2
    assert response.json['items'][0]['org_name'] == 'Wheel'