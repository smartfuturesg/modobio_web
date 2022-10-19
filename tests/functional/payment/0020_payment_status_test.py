from flask.json import dumps

from .data import payment_status_data, payment_status_auth_header

@pytest.mark.skip('payment disabled until instamed is replaced')
def test_post_payment_status(test_client):
    payment_status_data['valid_data']['user_id'] = test_client.client_id

    #test with invalid authorization, should raise 401
    response = test_client.post(
        '/payment/status/',
        headers={},
        data=dumps(payment_status_data['valid_data']),
        content_type='application/json')

    assert response.status_code == 401

    response = test_client.post(
        '/payment/status/',
        headers=payment_status_auth_header,
        data=dumps(payment_status_data['invalid_user_id']),
        content_type='application/json')

    assert response.status_code == 400

    response = test_client.post(
        '/payment/status/',
        headers=payment_status_auth_header,
        data=dumps(payment_status_data['valid_data']),
        content_type='application/json')

    assert response.status_code == 200
    assert response.get_json()['original_transaction_id'] == "HASDYF7SDFYAF"

@pytest.mark.skip('payment disabled until instamed is replaced')
def test_get_payment_status(test_client):
    response = test_client.get(
        f'/payment/status/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
