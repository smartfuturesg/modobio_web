import pytest

from flask.json import dumps
from datetime import datetime, timezone, timedelta

from odyssey.api.payment.models import PaymentMethods
from odyssey.api.telehealth.models import TelehealthBookingStatus, TelehealthBookings

from odyssey.utils.misc import get_time_index

from .data import payment_methods_data


@pytest.fixture(scope='module')
def test_payment_method(test_client):
    response = test_client.post(
        f'/payment/methods/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payment_methods_data['normal_data']),
        content_type='application/json')
    
    payment_method = PaymentMethods.query.filter_by(idx=response.json['idx']).one_or_none()
    
    yield payment_method
    
    test_client.db.session.delete(payment_method)
    test_client.db.session.commit()

@pytest.fixture(scope='function')
def test_booking(test_client, test_payment_method):
    """
    This function will generate a booking object for a booking that is less than 24 hours away.
    This can be used to test the payment system.
    """

    #find UTC time window that is closest to current time plus 1 hour
    target_time = datetime.now(timezone.utc) + timedelta(hours=1)
    target_time_id = get_time_index(target_time)

    #prevent a time slot that would loop to the next day
    if target_time_id >= 285:
        target_time_id = 284

    booking = TelehealthBookings(**{
        'payment_method_id': test_payment_method.idx,
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
        'consult_rate': 99.00,
        'scheduled_duration_mins': 20
    })

    test_client.db.session.add(booking)
    test_client.db.session.flush()

    yield booking

    statuses = TelehealthBookingStatus.query.filter_by(booking_id=booking.idx).all()
    for status in statuses:
        test_client.db.session.delete(status)
    test_client.db.session.delete(booking)
    test_client.db.session.commit()