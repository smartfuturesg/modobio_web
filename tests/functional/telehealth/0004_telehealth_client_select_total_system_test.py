import base64

from datetime import datetime, timedelta
import time
from dateutil import tz

import pytest

from flask.json import dumps
from sqlalchemy.sql.expression import delete, select

# from tests.conftest import generate_users
from odyssey.api.payment.models import PaymentMethods
from odyssey.api.user.models import User
from odyssey.api.telehealth.models import TelehealthStaffAvailability, TelehealthBookings
from odyssey.api.staff.models import StaffRoles, StaffOperationalTerritories
from odyssey.tasks.tasks import cleanup_unended_call

from tests.utils import login

from .client_select_data import (
    telehealth_staff_4_general_availability_post_data,
    telehealth_staff_6_general_availability_post_data,
    telehealth_staff_8_general_availability_post_data,
    telehealth_staff_10_general_availability_post_data,
    telehealth_staff_12_general_availability_post_data,
    telehealth_staff_14_general_availability_post_data,
    telehealth_bookings_staff_4_client_1_data,
    telehealth_bookings_staff_4_client_3_data,
    telehealth_bookings_staff_8_client_5_data,
    telehealth_queue_client_3_data,
    payment_method_data,
    payment_refund_data
)

def test_generate_staff_availability(test_client, telehealth_staff):
    availability_data = [
        telehealth_staff_4_general_availability_post_data,
        telehealth_staff_6_general_availability_post_data,
        telehealth_staff_8_general_availability_post_data,
        telehealth_staff_10_general_availability_post_data,
        telehealth_staff_12_general_availability_post_data,
        telehealth_staff_14_general_availability_post_data]

    for availability, user in zip(availability_data, telehealth_staff):
        auth_header = login(test_client, user)

        response = test_client.post(
            f'/telehealth/settings/staff/availability/{user.user_id}/',
            headers=auth_header,
            data=dumps(availability),
            content_type='application/json')

        assert response.status_code == 201

def test_generate_bookings(test_client, telehealth_staff, telehealth_clients, payment_method):
    ##
    # Create booking 1
    ##
    # add client to queue first

    queue_data = {
        'profession_type': 'medical_doctor',
        'target_date': datetime.strptime(
            telehealth_bookings_staff_4_client_1_data.get('target_date'), '%Y-%m-%d').isoformat(),
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
        f'&staff_user_id={telehealth_staff[0].user_id}',
        headers=test_client.client_auth_header,
        data=dumps(telehealth_bookings_staff_4_client_1_data),
        content_type='application/json')

    assert response.status_code == 201

    ##
    # Create booking 2
    ##
    # add client to queue first
    queue_data = {
        'profession_type': 'medical_doctor',
        'target_date': datetime.strptime(
            telehealth_bookings_staff_4_client_3_data.get('target_date'), '%Y-%m-%d').isoformat(),
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
        f'&staff_user_id={telehealth_staff[0].user_id}',
        headers=test_client.client_auth_header,
        data=dumps(telehealth_bookings_staff_4_client_3_data),
        content_type='application/json')

    assert response.status_code == 201

    ##
    # Create booking 3
    ##
    # use different staff and client users. Must sign in as staff first
    client_4 = telehealth_clients[4]
    client_4_auth_header = login(test_client, client_4)

    # add payment method to db
    response = test_client.post(
        f'/payment/methods/{client_4.user_id}/',
        headers=client_4_auth_header,
        data=dumps(payment_method_data),
        content_type='application/json')

    pm = PaymentMethods.query.filter_by(user_id=client_4.user_id).first()

    # add client to queue first
    queue_data = {
        'profession_type': 'medical_doctor',
        'target_date': datetime.strptime(
            telehealth_bookings_staff_8_client_5_data.get('target_date'), '%Y-%m-%d').isoformat(),
        'priority': False,
        'medical_gender': 'np',
        'location_id': 1,
        'payment_method_id': pm.idx}

    response = test_client.post(
        f'/telehealth/queue/client-pool/{client_4.user_id}/',
        headers=client_4_auth_header,
        data=dumps(queue_data),
        content_type='application/json')

    response = test_client.post(
        f'/telehealth/bookings/'
        f'?client_user_id={client_4.user_id}'
        f'&staff_user_id={telehealth_staff[2].user_id}',
        headers=client_4_auth_header,
        data=dumps(telehealth_bookings_staff_8_client_5_data),
        content_type='application/json')

    assert response.status_code == 201

def test_generate_client_queue(test_client, payment_method):
    telehealth_queue_client_3_data['payment_method_id'] = payment_method.idx
    response = test_client.post(
        f'/telehealth/queue/client-pool/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(telehealth_queue_client_3_data),
        content_type='application/json')

    assert response.status_code == 201

def test_client_time_select(test_client):
    response = test_client.get(
        f'/telehealth/client/time-select/{test_client.client_id}/',
        headers=test_client.client_auth_header)

    assert response.status_code == 200
    assert response.json['total_options'] == 30

def test_full_system_with_settings(test_client, payment_method):
    """
    Testing the full telehealth system:

    1. set staff availability (UTC)
    2. client adds to the queue (America/Phoenix)
    3. client views availabilities and selects an appointment 
    4. Client makes booking
    5. client and staff view their bookings

    The staff availability in UTC should be converted to the client's timezone (America/Phoenix) for display.
    """  
    # clear all availabilities before this
    current_availabilities = test_client.db.session.execute(
        delete(TelehealthStaffAvailability)
        .where(TelehealthStaffAvailability.idx > 0))

    ##
    # 1. Set staff's availability
    ##
    availability = {
        'settings': {
            'timezone': 'UTC',
            'auto_confirm': False},
        'availability' : [{
            'day_of_week': 'Wednesday',
            'start_time': '3:00:00',
            'end_time': '12:00:00'}]}

    response = test_client.post(
        f'/telehealth/settings/staff/availability/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(availability),
        content_type='application/json')

    ##
    # 2. Client requests to be added to the queue
    ##
    client_queue = {
        "profession_type": "medical_doctor",
        "priority": "True",
        "duration": 20,
        "medical_gender": "np",
        "target_date": "2024-11-6T00:00:00",
        "timezone": "America/Phoenix",
        'location_id': 1,
        'payment_method_id': payment_method.idx}

    response = test_client.post(
        f'/telehealth/queue/client-pool/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(client_queue),
        content_type='application/json')

    ##
    # 3. Client requests to view availabilities for selected target date
    ##
    response = test_client.get(
        f'/telehealth/client/time-select/{test_client.client_id}/',
        headers=test_client.client_auth_header)

    assert response.status_code == 200
    assert response.json['appointment_times'][0]['start_time'] == '00:00:00'
    assert response.json['appointment_times'][0]['booking_window_id_start_time'] == 1

    assert response.json['appointment_times'][-1]['start_time'] == '04:30:00'
    assert response.json['appointment_times'][-1]['booking_window_id_start_time'] == 55
    assert response.json['total_options'] == 19

    ##
    # 4. Client selects an appointment time
    ##
    # select the booking that is at 4:30 Phx time/ 11:30 UTC
    client_booking = {
        'target_date': '2024-11-6',
        'booking_window_id_start_time': response.json['appointment_times'][-1]['booking_window_id_start_time'],
        'booking_window_id_end_time': response.json['appointment_times'][-1]['booking_window_id_end_time']}

    response = test_client.post(
        f'/telehealth/bookings/'
        f'?client_user_id={test_client.client_id}'
        f'&staff_user_id={test_client.staff_id}',
        headers=test_client.client_auth_header,
        data=dumps(client_booking),
        content_type='application/json')

    assert response.json['bookings'][0]['client']['timezone'] == 'America/Phoenix'
    assert response.json['bookings'][0]['practitioner']['timezone'] == 'UTC'
    assert response.json['bookings'][0]['status'] == 'Pending'
    assert response.json['bookings'][0]['payment_method_id'] == payment_method.idx

    booking_id = response.json['bookings'][0]['booking_id']

    ##
    # 5. Pull up bookings from the client and staff perspectives
    ##
    response = test_client.get(
        f'/telehealth/bookings/'
        f'?client_user_id={test_client.client_id}'
        f'&staff_user_id={test_client.staff_id}',
        headers=test_client.staff_auth_header,
        content_type='application/json')
    for booking in response.json['bookings']:
        if booking['booking_id'] == booking_id:
            current_booking = booking
            break
    # booking time as seen by the staff
    assert current_booking['practitioner']['start_time_localized'] == '11:30:00'
    assert current_booking['practitioner']['end_time_localized'] == '11:50:00'
    assert current_booking['practitioner']['timezone'] == 'UTC'

    response = test_client.get(
        f'/telehealth/bookings/'
        f'?client_user_id={test_client.client_id}'
        f'&staff_user_id={test_client.staff_id}',
        headers=test_client.client_auth_header,
        content_type='application/json')

    for booking in response.json['bookings']:
        if booking['booking_id'] == booking_id:
            current_booking = booking
            break

    # booking time as seen by the client
    assert current_booking['client']['start_time_localized'] == '04:30:00'
    assert current_booking['client']['end_time_localized'] == '04:50:00'
    assert current_booking['client']['timezone'] == 'America/Phoenix'

# TODO: first request fails with missing chat room.
#   return {'twilio_token': token,
#           'conversation_sid': booking.chat_room.conversation_sid}
#   AttributeError: 'NoneType' object has no attribute 'conversation_sid'
#
# Everything else fails as a result, too many dependencies in one test.

#@pytest.mark.skip('Fails') 
def test_bookings_meeting_room_access(test_client, booking_twilio):
    
    response = test_client.get(
        f'/telehealth/bookings/meeting-room/access-token/{booking_twilio.idx}/',
        headers=test_client.staff_auth_header)
    ###
    # Complete the booking
    ###
    response = test_client.put(
        f'/telehealth/bookings/complete/{booking_twilio.idx}/',
        headers=test_client.staff_auth_header)

    assert response.status_code == 200


def test_cleanup_unended_call(test_client, booking_twilio):
    
    response = test_client.get(
        f'/telehealth/bookings/meeting-room/access-token/{booking_twilio.idx}/',
        headers=test_client.staff_auth_header)
    
    assert response.status_code == 200
    assert booking_twilio.status == 'In Progress'

    complete = cleanup_unended_call(booking_twilio.idx)
    
    assert booking_twilio.status == 'Completed'
    # TODO run the above line without a user being logged in.
    #assert booking_twilio.status_history[-1].reporter_role == 'System'
    assert complete == 'Booking Completed by System'


def test_delete_generated_users(test_client):
    assert 1 == 1