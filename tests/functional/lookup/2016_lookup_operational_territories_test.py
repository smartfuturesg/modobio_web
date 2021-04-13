from flask.json import dumps

def test_get_transaction_types(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for lookup transaction types
    WHEN the '/lookup/business/transaction-types/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/lookup/operational-territories/',
                                headers=client_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200
    assert response.json['total_items'] == 29