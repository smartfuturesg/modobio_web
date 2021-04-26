from flask.json import dumps

def test_get_terms_and_conditions(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for lookup terms and conditions
    WHEN the '/lookup/terms-and-conditions/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/lookup/terms-and-conditions/',
                                headers=client_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200
    assert response.json['terms_and_conditions'] == 'Terms and Conditions'