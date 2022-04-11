
from datetime import datetime, timedelta

from flask.json import dumps

from odyssey.api.payment.models import PaymentMethods
from odyssey.api.telehealth.models import TelehealthBookingDetails, TelehealthBookings, TelehealthChatRooms, TelehealthStaffAvailability
from odyssey.tasks.tasks import cleanup_unended_call
from flask import g

from tests.utils import login

from .data import target_date_next_monday

from .client_select_data import (
    telehealth_staff_4_general_availability_post_data,
    telehealth_staff_6_general_availability_post_data,
    telehealth_staff_8_general_availability_post_data,
    telehealth_staff_10_general_availability_post_data,
    telehealth_staff_12_general_availability_post_data,
    telehealth_staff_14_general_availability_post_data,
    telehealth_booking_data_1,
    telehealth_booking_data_2,
    telehealth_booking_data_3,
    telehealth_queue_client_3_data,
    payment_method_data
)

def test_generate_client_queue(test_client, payment_method):
    telehealth_queue_client_3_data['payment_method_id'] = payment_method.idx
    response = test_client.post(
        f'/telehealth/queue/client-pool/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(telehealth_queue_client_3_data),
        content_type='application/json')

    assert response.status_code == 201

def test_client_time_select(test_client, staff_availabilities):

    response = test_client.get(
        f'/telehealth/client/time-select/{test_client.client_id}/',
        headers=test_client.client_auth_header)

    assert response.status_code == 200
    assert response.json['total_options'] == 95

def test_generate_staff_availability(test_client, telehealth_staff):
    """
    fill up the staff availabilities
    add client to queue
    view current availabilities
    """
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

def test_generate_bookings(test_client, telehealth_staff, telehealth_clients, payment_method, staff_availabilities):

    ##
    # Create booking 1
    ##
    # add client to queue first

    queue_data = {
        'profession_type': 'medical_doctor',
        'target_date': datetime.strptime(
                telehealth_booking_data_1.get('target_date'), '%Y-%m-%d').isoformat(),
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
        data=dumps(telehealth_booking_data_1),
        content_type='application/json')

    assert response.status_code == 201

    ##
    # Create booking 2
    ##
    # add client to queue first
    queue_data = {
        'profession_type': 'medical_doctor',
        'target_date': datetime.strptime(
                telehealth_booking_data_2.get('target_date'), '%Y-%m-%d').isoformat(),
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
        data=dumps(telehealth_booking_data_2),
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
                telehealth_booking_data_3.get('target_date'), '%Y-%m-%d').isoformat(),
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
        data=dumps(telehealth_booking_data_3),
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

def test_client_time_select(test_client, staff_availabilities):
    response = test_client.get(
        f'/telehealth/client/time-select/{test_client.client_id}/',
        headers=test_client.client_auth_header)
        
    assert response.status_code == 200
    assert response.json['total_options'] == 95

def test_full_system_with_settings(test_client, payment_method, telehealth_staff):
    """
    Testing the full telehealth system:

    1. set staff availability (UTC)
    2. client adds to the queue (America/Phoenix)
    3. client views availabilities and selects an appointment 
    4. Client makes booking
    5. client and staff view their bookings

    The staff availability in UTC should be converted to the client's timezone (America/Phoenix) for display.
    """  
    staff_login = login(test_client, telehealth_staff[0])
    # clear all availabilities and bookings before this
    test_client.db.session.query(TelehealthStaffAvailability).delete()
    test_client.db.session.query(TelehealthChatRooms).delete()
    test_client.db.session.query(TelehealthBookingDetails).delete()
    test_client.db.session.query(TelehealthBookings).delete()
    test_client.db.session.commit()

    ##
    # 1. Set staff's availability
    ##
    availability = {
        'settings': {
            'timezone': 'UTC',
            'auto_confirm': False},
        'availability' : [{
            'day_of_week': 'Monday',
            'start_time': '3:00:00',
            'end_time': '12:00:00'}]}

    response = test_client.post(
        f'/telehealth/settings/staff/availability/{telehealth_staff[0].user_id}/',
        headers=staff_login,
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
        "target_date": (target_date_next_monday + timedelta(weeks=1)).isoformat(),
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
        'target_date': target_date_next_monday.date().isoformat(),
        'booking_window_id_start_time': response.json['appointment_times'][-1]['booking_window_id_start_time'],
        'booking_window_id_end_time': response.json['appointment_times'][-1]['booking_window_id_end_time']}

    response = test_client.post(
        f'/telehealth/bookings/'
        f'?client_user_id={test_client.client_id}'
        f'&staff_user_id={telehealth_staff[0].user_id}',
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
        f'&staff_user_id={telehealth_staff[0].user_id}',
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


def test_booking_start_and_complete(test_client, booking_function_scope):
    
    # start teelehealth call as a staff member
    response = test_client.get(
        f'/telehealth/bookings/meeting-room/access-token/{booking_function_scope.idx}/',
        headers=test_client.staff_auth_header)

    assert response.status_code == 200

    ###
    # Complete the booking
    ###
    response = test_client.put(
        f'/telehealth/bookings/complete/{booking_function_scope.idx}/',
        headers=test_client.staff_auth_header)

    assert response.status_code == 200


def test_booking_start_fail(test_client, booking_function_scope):
    
    # bookings cannot be started by a client, ensure this is the case by making the request below
    response = test_client.get(
        f'/telehealth/bookings/meeting-room/access-token/{booking_function_scope.idx}/',
        headers=test_client.client_auth_header)

    assert response.status_code == 400

    # change the timing of the call so that it has already ended
    # meetings cannot begin after the scheduled duration has passed
    booking_function_scope.target_date_utc = booking_function_scope.target_date_utc - timedelta(days=1)

    test_client.db.session.add(booking_function_scope)
    test_client.db.session.commit()

    response = test_client.get(
        f'/telehealth/bookings/meeting-room/access-token/{booking_function_scope.idx}/',
        headers=test_client.staff_auth_header)

    assert response.status_code == 400


def test_cleanup_unended_call(test_client, booking_function_scope):
    
    response = test_client.get(
        f'/telehealth/bookings/meeting-room/access-token/{booking_function_scope.idx}/',
        headers=test_client.staff_auth_header)
    
    assert response.status_code == 200
    assert booking_function_scope.status == 'In Progress'

    g.flask_httpauth_user = None
    complete = cleanup_unended_call(booking_function_scope.idx)
    
    assert booking_function_scope.status == 'Completed'
    assert booking_function_scope.status_history[-1].reporter_role == 'System'
    assert complete == 'Booking Completed by System'


def test_delete_generated_users(test_client):
    assert 1 == 1