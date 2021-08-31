from flask.json import dumps

from .data import payment_methods_data, payment_booking_data

from odyssey.api.telehealth.models import TelehealthBookings
from odyssey import db

"""
This file will be a complete test of the payment system.  In order to accomplish this we need to:

1) Add up to 5 payment methods for a user
2) View the user's payment methods
3) Delete one of the user's payment methods
4) Create a telehealth booking for the user using one of their saved payment methods
5) Start the booking and ensure the user was charged.
6) Ensure the payment shows up in the user's payment history
7) Process refunds for the payment from above

We also have to cover all possible error cases during all of the above steps.
"""

def test_payment_system(test_client):

    """Step 1 Add Payment Methods"""

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

    assert response.status_code == 405

    """Step 2 View Payment Methods"""

    response = test_client.get(
        f'/payment/methods/{test_client.client_id}/',
        headers = test_client.client_auth_header,
        content_type='application.json')

    assert response.status_code == 200
    assert len(response.json) == 5
    assert response.json[0]['expiration'] == '04/25'

    """Step 3 Delete Payment Methods"""

    #attempt to delete with invalid idx
    response = test_client.delete(
        f'/payment/methods/{test_client.client_id}/?idx=999',
        headers = test_client.client_auth_header,
        content_type='application.json')

    assert response.status_code == 404

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

    """Step 4 Create Booking"""

    #booking being created directly for simplicity. The correct endpoints for creating and working
    #with bookings are tested within the 'telehealth' test namespace
    payment_booking_data['client_user_id'] = test_client.client_id
    payment_booking_data['staff_user_id'] = test_client.staff_id

    db.session.add(TelehealthBookings(**payment_booking_data))

    """Step 5 Start Booking"""
    booking_id = TelehealthBookings.query.first().idx

    response = test_client.get(
        f'/telehealth/bookings/meeting-room/access-token/{booking_id}/',
        headers = test_client.staff_auth_header,
        content_type='application.json')


    print(response.data)
    assert response.status_code == 200

    """Step 6 View History"""
    response = test_client.get(
        f'/payment/history/{test_client.client_id}/',
        headers = test_client.client_auth_header,
        content_type='application.json')

    assert response.status_code == 200
    assert response[0]['payment_method_id'] == 1

    """Step 7 Process Refunds"""

    response = test_client.post(
        f'/payment/refunds/{test_client.client_id}/',
        headers = test_client.client_auth_header,
        content_type='application.json')

    assert response.status_code == 201

    response = test_client.post(
        f'/payment/refunds/{test_client.client_id}/',
        headers = test_client.client_auth_header,
        content_type='application.json')

    assert response.status_code == 201

    response = test_client.post(
        f'/payment/refunds/{test_client.client_id}/',
        headers = test_client.client_auth_header,
        content_type='application.json')

    assert response.status_code == 405