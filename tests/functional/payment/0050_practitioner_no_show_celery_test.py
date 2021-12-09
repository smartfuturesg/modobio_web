import pytest
from datetime import datetime, timezone, timedelta
from flask.json import dumps, loads

from odyssey.api.lookup.models import LookupBookingTimeIncrements
from odyssey.api.payment.models import PaymentHistory
from odyssey.api.telehealth.models import TelehealthBookings

from odyssey.tasks.periodic import detect_practitioner_no_show

from .data import test_booking
from odyssey import db

def test_no_show_scan(test_client, test_booking):
    #set booking to 10 mins ago
    booking_id = test_booking.idx
    target_time = datetime.now(timezone.utc)
    if target_time.minute % 5 != 0:
        minutes = target_time.minute + 5 - target_time.minute % 5
        if minutes > 60:
            minutes = 0
        target_time.replace(minute=minutes)
    target_time = target_time.replace(second=0, microsecond=0)
        
    target_time_window = LookupBookingTimeIncrements.query \
        .filter(LookupBookingTimeIncrements.start_time == target_time.time()).first().idx
    
    if target_time_window <= 1:
        #if it is 12:00 or 12:05, we have to adjust to target the previous date at 11:50 and 11:55 respectively
        target_time = target_time - timedelta(hours=24)
        target_time_window = 289 + target_time_window
    
    target_time_window -= 2
    test_booking.booking_window_id_start_time_utc = target_time_window
        
    #charge the booking
    response = test_client.post(
        '/payment/test/charge/',
        headers=test_client.staff_auth_header,
        data=dumps({'booking_id': booking_id}),
        content_type='application/json')

    #should succeed
    res = loads(response.data)
    assert response.status_code == 200
    assert res['TransactionStatus'] == "C"
    assert test_booking.charged
    
    #deploy task and make sure task booking is canceled
    assert test_booking.status == 'Accepted'
    detect_practitioner_no_show()
    
    booking = TelehealthBookings.query.filter_by(idx=booking_id).one_or_none()
    assert booking.status == 'Canceled'
    
    #check that client was refunded
    payment = PaymentHistory.query.filter_by(booking_id=booking_id).one_or_none()
    assert payment.voided == True
    assert payment.void_reason == 'Practitioner No Show'