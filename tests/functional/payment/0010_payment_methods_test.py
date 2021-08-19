from flask.json import dumps

from .data import payment_methods_data

def test_post_payment_method(test_client):
    #test with invalid card #, should raise 400
    response = test_client.post(
        f'/payment/methods/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payment_methods_data['invalid_card']),
        content_type='application/json')

    assert response.status_code == 400

    #test with expired card, should raise 400
    response = test_client.post(
        f'/payment/methods/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payment_methods_data['expired']),
        content_type='application/json')

    assert response.status_code == 400

    #test with valid card details
    response = test_client.post(
        f'/payment/methods/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payment_methods_data['normal_data']),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['payment_type'] == 'VISA'
    assert response.json['is_default'] == True

    #test again with valid card details and set new card to default
    response = test_client.post(
        f'/payment/methods/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payment_methods_data['normal_data_2']),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['payment_type'] == 'MC'
    assert response.json['is_default'] == True

    # Test adding too many payment methods, should return 405 when attemping to add 6th payment
    # First card was added by database/0001_seed_users.sql
    response = test_client.post(
        f'/payment/methods/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payment_methods_data['normal_data_3']),
        content_type='application/json')

    assert response.status_code == 201

    response = test_client.post(
        f'/payment/methods/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payment_methods_data['normal_data_3']),
        content_type='application/json')

    assert response.status_code == 201

    response = test_client.post(
        f'/payment/methods/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payment_methods_data['normal_data_3']),
        content_type='application/json')

    assert response.status_code == 405

def test_get_payment_method(test_client):
    response = test_client.get(
        f'/payment/methods/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json[1]['payment_type'] == 'VISA'
    assert response.json[1]['is_default'] == False
    assert response.json[2]['payment_type'] == 'MC'
    assert response.json[2]['is_default'] == True

def test_delete_payment_method(test_client):
    #test with valid idx
    response = test_client.delete(
        f'/payment/methods/{test_client.client_id}/?idx=1',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 204

    #test with invalid idx
    response = test_client.delete(
        f'/payment/methods/{test_client.client_id}/?idx=20',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 404

    #test with non-numeric idx
    response = test_client.delete(
        f'/payment/methods/{test_client.client_id}/?idx=test',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 404
