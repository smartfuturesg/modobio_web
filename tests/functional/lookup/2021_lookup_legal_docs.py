from flask.json import dumps

def test_get_legal_docs(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for lookup terms and conditions
    WHEN the '/lookup/terms-and-conditions/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/lookup/legal-docs/',
                                headers=client_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200
    assert response.json['total_items'] == 2
    assert response.json['items'][1]['name'] == 'Terms of Use'
    assert response.json['items'][0]['name'] == 'Privacy Policy'