from flask.json import dumps

from .data import payment_methods_data

from odyssey.api.telehealth.models import TelehealthBookings
from odyssey import db

def test_payment_methods_post(test_client):

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

    assert response.status_code == 201

    response = test_client.post(
        f'/payment/methods/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payment_methods_data['normal_data_3']),
        content_type='application/json')

    assert response.status_code == 400

def test_payment_methods_get(test_client):

    response = test_client.get(
        f'/payment/methods/{test_client.client_id}/',
        headers = test_client.client_auth_header,
        content_type='application.json')

    assert response.status_code == 200
    assert len(response.json) == 5
    assert response.json[0]['expiration'] == '04/25'

def test_payment_methods_delete(test_client):

    #attempt to delete with invalid idx
    response = test_client.delete(
        f'/payment/methods/{test_client.client_id}/?idx=999',
        headers = test_client.client_auth_header,
        content_type='application.json')

    assert response.status_code == 204

    response = test_client.delete(
        f'/payment/methods/{test_client.client_id}/?idx=5',
        headers = test_client.client_auth_header,
        content_type='application.json')

    assert response.status_code == 204

    response = test_client.get(
        f'/payment/methods/{test_client.client_id}/',
        headers = test_client.client_auth_header,
        content_type='application.json')

    assert response.status_code == 200
    assert len(response.json) == 4