import pytest

from datetime import datetime, time, timezone, timedelta

from odyssey import db
from odyssey.api.lookup.models import LookupBookingTimeIncrements
from odyssey.api.telehealth.models import TelehealthBookings
from odyssey.api.payment.models import PaymentMethods

payment_methods_data = {
    'normal_data': {
        'token': '4111111111111111',
        'expiration': '04/25',
        'is_default': True
    },
    'normal_data_2': {
        'token': '5500000000000004',
        'expiration': '04/25',
        'is_default': True
    },
    'normal_data_3': {
        'token': '6011000000000004',
        'expiration': '04/25',
        'is_default': False
    },
    'invalid_card': {
        'token': '9999999999999999',
        'expiration': '04/25',
        'is_default': True
    },
    'expired': {
        'token': '4111111111111111',
        'expiration': '01/20',
        'is_default': False
    }
}

payment_status_auth_header = {
    'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0dHlwZSI6Im9yZ2FuaXphdGlvbiIsIm9uYW1lIjoiSW5zdGFNZWQifQ.BGQgeZ_vAO40S1rjDusPCu1DAGryyBulm1i72E9ze4Q'
}

payment_status_data = {
    'invalid_user_id': {
        "user_id": 99,
        "original_transaction_status_code": "C",
        "card_present_status": "NotPresentInternet",
        "transaction_action": "Sale",
        "save_on_file_transaction_id": "BASJDNFSA76YASD",
        "original_transaction_id": "HASDYF7SDFYAF",
        "payment_transaction_id": "SDFHUASDF67IA",
        "request_amount": "10.99",
        "current_transaction_status_code": "C"
    },
    'valid_data': {
        "user_id": 1,
        "original_transaction_status_code": "C",
        "card_present_status": "NotPresentInternet",
        "transaction_action": "Sale",
        "save_on_file_transaction_id": "BASJDNFSA76YASD",
        "original_transaction_id": "HASDYF7SDFYAF",
        "payment_transaction_id": "SDFHUASDF67IA",
        "request_amount": "10.99",
        "current_transaction_status_code": "C"
    }
}

payment_refund_data = {
  "refund_amount":"49.50",
  "payment_id": 1,
  "refund_reason": "abcdefghijklmnopqrstuvwxyz"
}

@pytest.fixture(scope='function')
def test_booking(test_client):
    """
    This function will generate a booking object for a booking that is less than 24 hours away.
    This can be used to test the payment system.
    """

    #find UTC time window that is closest to current time plus 1 hour
    target_time = datetime.now(timezone.utc) + timedelta(hours=1)
    target_time_id = LookupBookingTimeIncrements.query                \
        .filter(LookupBookingTimeIncrements.start_time <= target_time.time(), \
        LookupBookingTimeIncrements.end_time >= target_time.time()).one_or_none().idx

    #prevent a time slot that would loop to the next day
    if target_time_id >= 285:
        target_time_id = 284

    booking = TelehealthBookings(**{
        'payment_method_id': PaymentMethods.query.filter_by(user_id=test_client.client_id).first().idx,
        'client_user_id': test_client.client_id,
        'staff_user_id': test_client.staff_id,
        'profession_type': 'medical_doctor',
        'target_date': target_time.date(),
        'booking_window_id_start_time': target_time_id,
        'booking_window_id_end_time': target_time_id + 4,
        'booking_window_id_start_time_utc': target_time_id,
        'booking_window_id_end_time_utc': target_time_id + 4,
        'status': 'Accepted',
        'client_timezone': 'UTC',
        'staff_timezone': 'UTC',
        'target_date_utc': target_time.date(),
        'client_location_id': 1,
        'charged': False,
        'consult_rate': 99.00
    })

    test_client.db.session.add(booking)
    test_client.db.session.commit()

    yield booking

    for status in booking.status_history:
        test_client.db.session.delete(status)

    test_client.db.session.delete(booking)
    test_client.db.session.commit()