from datetime import datetime, time, timezone, timedelta

from flask.json import dumps

from odyssey import db
from odyssey.api.lookup.models import LookupBookingTimeIncrements
from odyssey.api.telehealth.models import TelehealthBookings
from odyssey.api.payment.models import PaymentMethods, PaymentHistory

from .client_select_data import payment_refund_data

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
def test_bookings_payment(test_client):
    #force a booking in less than 24 hours into bookings table
    payment_method_id = PaymentMethods.query.filter_by(user_id=test_client.client_id).first().idx

    #find UTC time window that is closest to current time
    target_time = datetime.now(timezone.utc) + timedelta(hours=1)
    target_time_id = LookupBookingTimeIncrements.query                \
        .filter(LookupBookingTimeIncrements.start_time <= target_time.time(), \
        LookupBookingTimeIncrements.end_time >= target_time.time()).one_or_none().idx

    #prevent a time slot that would loop to the next day
    if target_time_id >= 285:
        target_time_id == 284

    booking_data = {
        'client_user_id': test_client.client_id,
        'staff_user_id': test_client.staff_id,
        'profession_type': 'medical_doctor',
        'target_date': target_time.date(),
        'booking_window_id_start_time': target_time_id,
        'booking_window_id_end_time': target_time_id + 4,
        'booking_window_id_start_time_utc': target_time_id,
        'booking_window_id_end_time_utc': target_time_id + 4,
        'status': 'Confirmed',
        'client_timezone': 'UTC',
        'staff_timezone': 'UTC',
        'target_date_utc': target_time.date(),
        'client_location_id': 1,
        'payment_method_id': payment_method_id,
        'charged': False
    }

    booking = TelehealthBookings(**booking_data)
    db.session.add(booking)
    db.session.commit()

    #run celery tasks to find and charge bookings
    bookings = find_chargable_bookings()
    assert len(bookings) == 1

    charge_telehealth_appointment(booking.idx)

    #retrieve the latest booking between these 2 users, which is the one we inserted above
    updated_booking = TelehealthBookings.query.filter_by(idx=booking.idx).one_or_none()

    assert updated_booking.charged == True

    history = PaymentHistory.query. \
        filter_by(user_id=test_client.client_id, payment_method_id=payment_method_id) \
        .order_by(PaymentHistory.created_at.desc()).all()[-1]

    assert history.transaction_amount
    assert history.transaction_id

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
    assert response.json[0]['refund_amount'] == '50.00'
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
    #the purchase was $100 and $100 total has been refunded over the course of the previous
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