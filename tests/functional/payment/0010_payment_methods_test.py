from flask.json import dumps

from .data import payment_methods_data

def test_post_payment_method(test_client, init_database, client_auth_header):
    """
    GIVEN an api end point for adding payment methods 
    WHEN the '/payment/methods/<user_id>/' resource is requested (POST)
    THEN check the response is valid
    """

    #test with invalid card #, should raise 400
    response = test_client.post('/payment/methods/1/',
                                headers=client_auth_header,
                                data=dumps(payment_methods_data['invalid_card']),
                                content_type='application/json')
    
    assert response.status_code == 400

    #test with expired card, should raise 400
    response = test_client.post('/payment/methods/1/',
                                headers=client_auth_header,
                                data=dumps(payment_methods_data['expired']),
                                content_type='application/json')

    assert response.status_code == 400

    #test with valid card details
    response = test_client.post('/payment/methods/1/',
                                headers=client_auth_header,
                                data=dumps(payment_methods_data['normal_data']),
                                content_type='application/json')

    assert response.status_code == 201
    assert response.get_json()['payment_type'] == 'VISA'
    assert response.get_json()['is_default'] == True

    #test again with valid card details and set new card to default
    response = test_client.post('/payment/methods/1/',
                                headers=client_auth_header,
                                data=dumps(payment_methods_data['normal_data_2']),
                                content_type='application/json')

    assert response.status_code == 201
    assert response.get_json()['payment_type'] == 'MC'
    assert response.get_json()['is_default'] == True

    #test adding too many payment methods, should return 405 when attemping to add 6th payment
    response = test_client.post('/payment/methods/1/',
                                headers=client_auth_header,
                                data=dumps(payment_methods_data['normal_data_3']),
                                content_type='application/json')

    assert response.status_code == 201
                    
    response = test_client.post('/payment/methods/1/',
                headers=client_auth_header,
                data=dumps(payment_methods_data['normal_data_3']),
                content_type='application/json')

    assert response.status_code == 201

    response = test_client.post('/payment/methods/1/',
                headers=client_auth_header,
                data=dumps(payment_methods_data['normal_data_3']),
                content_type='application/json')

    assert response.status_code == 201

    response = test_client.post('/payment/methods/1/',
                headers=client_auth_header,
                data=dumps(payment_methods_data['normal_data_3']),
                content_type='application/json')

    assert response.status_code == 405

def test_get_payment_method(test_client, init_database, client_auth_header):
    """
    GIVEN an api end point for viewing payment methods
    WHEN the '/payment/methods/<user_id>/' resource is requested  (GET)
    THEN check the payment methods are returned
    """

    response = test_client.get('/payment/methods/1/',
                                headers=client_auth_header,
                                content_type='application/json')

    assert response.status_code == 200
    assert response.get_json()[0]['payment_type'] == 'VISA'
    assert response.get_json()[0]['is_default'] == False
    assert response.get_json()[1]['payment_type'] == 'MC'
    assert response.get_json()[1]['is_default'] == True

def test_delete_payment_method(test_client, init_database, client_auth_header):
    """
    GIVEN a api end points for removing a payment method
    WHEN the '/payment/methods/<idx>/' resource is requested (DELETE) 
    THEN check the payment method is removed
    """

    #test with valid idx
    response = test_client.delete('/payment/methods/1/',
                                headers=client_auth_header,
                                content_type='application/json')
    print(response.data)
    assert response.status_code == 204

    #test with invalid idx
    response = test_client.delete('/payment/methods/999/',
                                headers=client_auth_header,
                                content_type='application/json')

    assert response.status_code == 404