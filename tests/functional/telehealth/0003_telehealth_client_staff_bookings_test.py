from datetime import datetime, time
from flask.json import dumps
from sqlalchemy import select

from odyssey.api.telehealth.models import TelehealthChatRooms
from odyssey.api.staff.models import StaffCalendarEvents
from odyssey.api.payment.models import PaymentMethods

from .data import (
    telehealth_client_staff_bookings_post_1_data,
    telehealth_client_staff_bookings_post_2_data,
    telehealth_client_staff_bookings_post_3_data,
    telehealth_client_staff_bookings_post_4_data,
    telehealth_client_staff_bookings_post_5_data,
    telehealth_client_staff_bookings_post_6_data,
    telehealth_client_staff_bookings_put_1_data
)

def test_post_1_client_staff_bookings(test_client):
    response = test_client.post(
        f'/telehealth/bookings/'
        f'?client_user_id={test_client.client_id}'
        f'&staff_user_id={test_client.staff_id}',
        headers=test_client.client_auth_header,
        data=dumps(telehealth_client_staff_bookings_post_1_data),
        content_type='application/json')

    # Bring up conversation to ensure it was created for this booking
    conversation = (test_client.db.session.execute(
        select(TelehealthChatRooms)
        .where(
            TelehealthChatRooms.staff_user_id == test_client.staff_id,
            TelehealthChatRooms.client_user_id == test_client.client_id))
        .one_or_none()[0])

    assert response.status_code == 201
    assert conversation.staff_user_id == test_client.staff_id
    assert conversation.client_user_id == test_client.client_id
    assert conversation.booking_id == 1

    staff_events = (test_client.db.session.execute(
        select(StaffCalendarEvents)
        .where(
            StaffCalendarEvents.location == f'Telehealth_{conversation.booking_id}'))
        .one_or_none()[0])
        
    assert staff_events.start_date == datetime.strptime(telehealth_client_staff_bookings_post_1_data['target_date'],'%Y-%m-%d').date()
    assert staff_events.start_time == time(8, 15)
    assert staff_events.end_time == time(8, 35)

def test_post_2_client_staff_bookings(test_client, payment_method):
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

    response = test_client.post(
        f'/telehealth/bookings/'
        f'?client_user_id={test_client.client_id}'
        f'&staff_user_id={test_client.staff_id}',
        headers=test_client.client_auth_header,
        data=dumps(telehealth_client_staff_bookings_post_2_data),
        content_type='application/json')

    assert response.status_code == 201

def test_post_3_client_staff_bookings(test_client):
    response = test_client.post(
        f'/telehealth/bookings/'
        f'?client_user_id={test_client.client_id}'
        f'&staff_user_id={test_client.staff_id}',
        headers=test_client.client_auth_header,
        data=dumps(telehealth_client_staff_bookings_post_3_data),
        content_type='application/json')
    assert response.status_code == 400

def test_post_4_client_staff_bookings(test_client):
    response = test_client.post(
        f'/telehealth/bookings/'
        f'?client_user_id={test_client.client_id}'
        f'&staff_user_id={test_client.staff_id}',
        headers=test_client.client_auth_header,
        data=dumps(telehealth_client_staff_bookings_post_3_data),
        content_type='application/json')

    assert response.status_code == 400

def test_post_5_client_staff_bookings(test_client):
    response = test_client.post(
        f'/telehealth/bookings/'
        f'?client_user_id={test_client.client_id}'
        f'&staff_user_id={test_client.staff_id}',
        headers=test_client.client_auth_header,
        data=dumps(telehealth_client_staff_bookings_post_3_data),
        content_type='application/json')

    assert response.status_code == 400

def test_post_6_client_staff_bookings(test_client):
    response = test_client.post(
        f'/telehealth/bookings/'
        f'?client_user_id={test_client.client_id}'
        f'&staff_user_id={test_client.staff_id}',
        headers=test_client.client_auth_header,
        data=dumps(telehealth_client_staff_bookings_post_3_data),
        content_type='application/json')

    assert response.status_code == 400

def test_get_1_staff_bookings(test_client):
    response = test_client.get(
        f'/telehealth/bookings/'
        f'?staff_user_id={test_client.staff_id}',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200

def test_get_2_client_bookings(test_client):
    response = test_client.get(
        f'/telehealth/bookings/'
        f'?client_user_id={test_client.client_id}',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200

def test_get_3_staff_client_bookings(test_client):
    response = test_client.get(
        f'/telehealth/bookings/'
        f'?client_user_id={test_client.client_id}'
        f'&staff_user_id={test_client.staff_id}',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['bookings'][0]['status'] == 'Accepted'

def test_put_1_client_staff_bookings(test_client, booking):
    
    response = test_client.put(
        f'/telehealth/bookings/?booking_id={booking.idx}',
        headers=test_client.staff_auth_header,
        data=dumps(telehealth_client_staff_bookings_put_1_data),
        content_type='application/json')

    assert response.status_code == 201

    staff_events = (test_client.db.session.execute(
        select(StaffCalendarEvents)
        .where(
            StaffCalendarEvents.location == f'Telehealth_{booking.idx}'))
        .one_or_none())

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
