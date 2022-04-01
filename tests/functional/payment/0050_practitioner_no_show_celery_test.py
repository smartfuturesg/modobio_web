from datetime import datetime, timezone, timedelta
from flask.json import dumps, loads

from odyssey.api.payment.models import PaymentHistory
from odyssey.api.telehealth.models import TelehealthBookings

from odyssey.tasks.periodic import detect_practitioner_no_show
from odyssey.utils.misc import get_time_index


def test_no_show_scan(test_client, test_booking):
    #set booking to 10 mins ago
    booking_id = test_booking.idx
    target_time = datetime.now(timezone.utc)
    target_time_window = get_time_index(target_time)
    if target_time_window <= 2:
        #if it is 12:00 or 12:05, we have to adjust to target the previous date at 11:50 and 11:55 respectively
        target_time = target_time - timedelta(hours=24)
        target_time_window = 288 + target_time_window
    
    target_time_window -= 2
    test_booking.booking_window_id_start_time_utc = target_time_window
    test_booking.target_date_utc = target_time.date()

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