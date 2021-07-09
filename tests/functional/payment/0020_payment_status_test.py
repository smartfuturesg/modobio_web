from flask.json import dumps

from .data import payment_status_data, payment_status_auth_header

def test_post_payment_status(test_client, init_database):
    """
    GIVEN an api end point for adding payment status 
    WHEN the '/payment/status/' resource is requested (POST)
    THEN check the response is valid
    """

    #test with invalid authorization, should raise 401
    response = test_client.post('/payment/status/',
                                headers={},
                                data=dumps(payment_status_data['valid_data']),
                                content_type='application/json')

    assert response.status_code == 401

    response = test_client.post('/payment/status/',
                                headers=payment_status_auth_header,
                                data=dumps(payment_status_data['invalid_user_id']),
                                content_type='application/json')

    assert response.status_code == 404

    response = test_client.post('/payment/status/',
                            headers=payment_status_auth_header,
                            data=dumps(payment_status_data['valid_data']),
                            content_type='application/json')

    assert response.status_code == 200
    assert response.get_json()['original_transaction_id'] == "HASDYF7SDFYAF"

def test_get_payment_status(test_client, init_database, client_auth_header):
    """
    GIVEN an api end point for viewing payment status
    WHEN the '/payment/status/<user_id>/' resource is requested  (GET)
    THEN check the payment statuses are returned
    """

    response = test_client.get('/payment/status/1/',
                                headers=client_auth_header,
                                content_type='application/json')

    assert response.status_code == 200
    assert response.get_json()[0]['original_transaction_id'] == 'HASDYF7SDFYAF'