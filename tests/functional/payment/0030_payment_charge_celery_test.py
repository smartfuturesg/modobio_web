from flask.json import dumps

from odyssey import db
from odyssey.api.telehealth.models import TelehealthBookings
from odyssey.api.payment.models import PaymentHistory

from .data import payment_refund_data, test_booking, test_payment_method

from odyssey.tasks.periodic import find_chargable_bookings
from odyssey.tasks.tasks import charge_telehealth_appointment

"""
This test intends to test the full payment system. In order to accomplish this, we must:


Schedule a telehealth appointment less than 24 hours away.
Trigger the celery task to charge for appointments.
Check that the payment was triggered through the payment history table
Refund the payment
Check that the refund was successful
"""
def test_bookings_payment(test_client, test_booking):
    #run celery tasks to find and charge bookings
    bookings = find_chargable_bookings()
    assert len(bookings) == 1

    charge_telehealth_appointment(test_booking.idx)

    assert test_booking.charged == True

    history = PaymentHistory.query. \
        filter_by(user_id=test_client.client_id, payment_method_id=test_booking.payment_method_id) \
        .order_by(PaymentHistory.created_at.desc()).all()[-1]

    assert history.transaction_amount == test_booking.consult_rate
    assert history.transaction_id
    assert history.transaction_descriptor == 'Telehealth-MedicalDoctor-20mins'
    #process refunds for the payment
    response = test_client.post(
        f'/payment/refunds/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payment_refund_data),
        content_type='application.json'
    )

    assert response.status_code == 201

    response = test_client.get(
        f'/payment/refunds/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        content_type='application.json'
    )

    assert response.status_code == 200
    assert response.json[0]['refund_amount'] == '49.50'
    assert response.json[0]['refund_reason'] == "abcdefghijklmnopqrstuvwxyz"

    response = test_client.post(
        f'/payment/refunds/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payment_refund_data),
        content_type='application.json'
    )

    assert response.status_code == 201

    response = test_client.get(
        f'/payment/refunds/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application.json'
    )

    assert response.status_code == 200
    assert len(response.json) == 2

    #third try should error because we are trying to refund more than the original purchase amount
    #the purchase was $99 and $99 total has been refunded over the course of the previous
    #2 refund POSTs

    response = test_client.post(
        f'/payment/refunds/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payment_refund_data),
        content_type='application.json'
    )

    assert response.status_code == 400

    response = test_client.get(
        f'/payment/refunds/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application.json'
    )

    assert response.status_code == 200
    assert len(response.json) == 2