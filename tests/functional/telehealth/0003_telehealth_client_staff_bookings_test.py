from datetime import datetime, time, timedelta
from flask.json import dumps
from sqlalchemy import select

from odyssey.api.telehealth.models import TelehealthBookingDetails, TelehealthBookings, TelehealthChatRooms
from odyssey.api.staff.models import StaffCalendarEvents
from tests.utils import login

import pytest

from .data import (
    telehealth_client_staff_bookings_post_1_data,
    telehealth_client_staff_bookings_post_2_data,
    telehealth_client_staff_bookings_post_3_data,
    telehealth_client_staff_bookings_put_1_data
)

def test_post_1_client_staff_bookings(test_client, staff_availabilities, telehealth_staff, payment_method):
    # delete previous bookings
    test_client.db.session.query(TelehealthChatRooms).delete()
    test_client.db.session.query(TelehealthBookingDetails).delete()
    test_client.db.session.query(TelehealthBookings).delete()
    test_client.db.session.commit()

    # add client to queue first
    queue_data = {
        'profession_type': 'medical_doctor',
        'target_date': datetime.strptime(
            telehealth_client_staff_bookings_post_1_data.get('target_date'), '%Y-%m-%d').isoformat(),
        'priority': False,
        'medical_gender': 'np',
        'location_id': 1,
        'payment_method_id': payment_method.idx,
        'duration': 30}

    
    response = test_client.post(
        f'/telehealth/queue/client-pool/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(queue_data),
        content_type='application/json')

    telehealth_client_staff_bookings_post_1_data['payment_method_id'] = payment_method.idx
    response = test_client.post(
        f'/telehealth/bookings/'
        f'?client_user_id={test_client.client_id}'
        f'&staff_user_id={telehealth_staff[0].user_id}',
        headers=test_client.client_auth_header,
        data=dumps(telehealth_client_staff_bookings_post_1_data),
        content_type='application/json')

    
    assert response.status_code == 201
    assert response.json.get('bookings')[0].get('status') == 'Pending'

    booking_id = response.json['bookings'][0]['booking_id']

    # confirm the booking. Will add the booking to the practitioner's calendar
    response = test_client.put(
        f'/telehealth/bookings/?booking_id={booking_id}',
        headers=test_client.client_auth_header,
        data=dumps( {'status': 'Confirmed'}),
        content_type='application/json')

    # Bring up conversation to ensure it was created for this booking
    conversation = TelehealthChatRooms.query.filter_by(booking_id=booking_id).one_or_none()
    
    assert conversation.staff_user_id == telehealth_staff[0].user_id
    assert conversation.client_user_id == test_client.client_id

    staff_events = (test_client.db.session.execute(
        select(StaffCalendarEvents)
        .where(
            StaffCalendarEvents.location == f'Telehealth_{conversation.booking_id}'))
        .one_or_none()[0])
        
    assert staff_events.start_date == datetime.strptime(telehealth_client_staff_bookings_post_1_data['target_date'],'%Y-%m-%d').date()
    assert staff_events.start_time == time(8, 15)
    assert staff_events.end_time == time(8, 45)

def test_post_2_client_staff_bookings(test_client, payment_method, telehealth_staff, staff_availabilities):
    # add client to queue first
    queue_data = {
        'profession_type': 'medical_doctor',
        'target_date': datetime.strptime(
            telehealth_client_staff_bookings_post_2_data.get('target_date'), '%Y-%m-%d').isoformat(),
        'priority': False,
        'medical_gender': 'np',
        'location_id': 1,
        'payment_method_id': payment_method.idx}

    response = test_client.post(
        f'/telehealth/queue/client-pool/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(queue_data),
        content_type='application/json')

    telehealth_client_staff_bookings_post_2_data['payment_method_id'] = payment_method.idx
    response = test_client.post(
        f'/telehealth/bookings/'
        f'?client_user_id={test_client.client_id}'
        f'&staff_user_id={telehealth_staff[0].user_id}',
        headers=test_client.client_auth_header,
        data=dumps(telehealth_client_staff_bookings_post_2_data),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json.get('bookings')[0].get('status') == 'Pending'

def test_post_3_client_staff_bookings(test_client, telehealth_staff, staff_availabilities, payment_method):
    telehealth_client_staff_bookings_post_3_data['payment_method_id'] = payment_method.idx
    response = test_client.post(
        f'/telehealth/bookings/'
        f'?client_user_id={test_client.client_id}'
        f'&staff_user_id={telehealth_staff[0].user_id}',
        headers=test_client.client_auth_header,
        data=dumps(telehealth_client_staff_bookings_post_3_data),
        content_type='application/json')

    # booking fails because client is not in queue
    assert response.status_code == 400

def test_get_1_staff_bookings(test_client, telehealth_staff):
    staff_header = login(test_client, telehealth_staff[0])
    response = test_client.get(
        f'/telehealth/bookings/'
        f'?staff_user_id={telehealth_staff[0].user_id}',
        headers=staff_header,
        content_type='application/json')

    assert response.status_code == 200

def test_get_2_client_bookings(test_client):
    response = test_client.get(
        f'/telehealth/bookings/'
        f'?client_user_id={test_client.client_id}',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200

def test_get_3_staff_client_bookings(test_client, telehealth_staff):
    response = test_client.get(
        f'/telehealth/bookings/'
        f'?client_user_id={test_client.client_id}'
        f'&staff_user_id={telehealth_staff[0].user_id}',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['bookings'][0]['status'] == 'Accepted'
    
#@pytest.mark.skip('randomly failing on pipeline but not locally')
def test_put_1_client_staff_bookings(test_client, booking):
    
    chat = TelehealthChatRooms.query.filter_by(booking_id=booking.idx).one_or_none()
    assert chat.conversation_sid != None
    
    response = test_client.put(
        f'/telehealth/bookings/?booking_id={booking.idx}',
        headers=test_client.staff_auth_header,
        data=dumps(telehealth_client_staff_bookings_put_1_data),
        content_type='application/json')
    
    assert chat.conversation_sid == None

    assert response.status_code == 201


def test_put_confirm_client_staff_booking(test_client, booking):
    """confirm the booking from the staff and client ends. 
    Staff cannot confirm the booking
    Client will not be able to confirm booking.Booking already Confirmed"""

    response = test_client.put(
        f'/telehealth/bookings/?booking_id={booking.idx}',
        headers=test_client.staff_auth_header,
        data=dumps( {'status': 'Confirmed'}),
        content_type='application/json')

    assert response.status_code == 401

    response = test_client.put(
        f'/telehealth/bookings/?booking_id={booking.idx}',
        headers=test_client.client_auth_header,
        data=dumps( {'status': 'Confirmed'}),
        content_type='application/json')

    assert response.status_code == 400


def test_put_2_client_staff_bookings(test_client, booking_function_scope):
    """
    Attempt to cancel a booking that has already started. should respond with 400
    """
    # change the timing of the call so that it has already ended
    booking_function_scope.target_date_utc = booking_function_scope.target_date_utc - timedelta(days=1)

    test_client.db.session.add(booking_function_scope)
    test_client.db.session.commit()

    response = test_client.put(
        f'/telehealth/bookings/?booking_id={booking_function_scope.idx}',
        headers=test_client.staff_auth_header,
        data=dumps(telehealth_client_staff_bookings_put_1_data),
        content_type='application/json')

    assert response.status_code == 400


def test_get_4_staff_client_bookings(test_client, booking):
    response = test_client.get(
        f'/telehealth/bookings/'
        f'?client_user_id={test_client.client_id}'
        f'&staff_user_id={test_client.staff_id}',
        headers=test_client.staff_auth_header,
        content_type='application/json')
        
    assert response.status_code == 200

    response_booking = None
    for bk in response.json['bookings']:
        if bk['booking_id'] == booking.idx:
            response_booking = bk
            break

    assert response_booking['status'] == booking.status
    assert response_booking['status_history'][0]['reporter_role'] == booking.status_history[0].reporter_role
