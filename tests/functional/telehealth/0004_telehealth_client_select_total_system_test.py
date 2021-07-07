
import base64
from datetime import datetime

from flask.json import dumps
import pytest
from sqlalchemy.sql.expression import delete, select

# from tests.conftest import generate_users
from odyssey.api.user.models import User
from odyssey.api.telehealth.models import TelehealthStaffAvailability
from odyssey.api.payment.models import PaymentMethods

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
    payment_method_data
)

# XXX: temporary fix for failing Twilio tests
# import pytest
# pytest.skip('Out of TwiliCoin.', allow_module_level=True)

def test_generate_staff_availability(test_client, init_database, generate_users, staff_auth_header):
    """
    GIVEN an api end point for looking client time select
    WHEN the  '/telehealth/client/time-select/<user_id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    global staff_users
    # Bring up some staff members
    staff_users = init_database.session.execute(
        select(User).where(User.email.in_([
                            'staff_member0@modobio.com',
                            'staff_member1@modobio.com',
                            'staff_member2@modobio.com',
                            'staff_member3@modobio.com',
                            'staff_member4@modobio.com',
                            'staff_member5@modobio.com'
                            ]))
    ).scalars().all()

    availability_data = [
    telehealth_staff_4_general_availability_post_data,
    telehealth_staff_6_general_availability_post_data,
    telehealth_staff_8_general_availability_post_data,
    telehealth_staff_10_general_availability_post_data,
    telehealth_staff_12_general_availability_post_data,
    telehealth_staff_14_general_availability_post_data
    ]
    for i, user in enumerate(staff_users):
        # sign in as user 
        valid_credentials = base64.b64encode(
            f"{user.email}:{'password'}".encode(
                "utf-8")).decode("utf-8")
        headers = {'Authorization': f'Basic {valid_credentials}'}

        response = test_client.post('/staff/token/',
                                headers=headers, 
                                content_type='application/json')
        token = response.json.get('token')
        auth_header = {'Authorization': f'Bearer {token}'}
  
        # GENERATE STAFF AVAILABILITY
        response = test_client.post(f'/telehealth/settings/staff/availability/{user.user_id}/',
                                    headers=auth_header, 
                                    data=dumps(availability_data[i]), 
                                    content_type='application/json')

        assert response.status_code == 201

def test_generate_bookings(test_client, init_database, client_auth_header):
    """
    GIVEN an api end point for looking client time select
    WHEN the  '/telehealth/bookings/' resource  is requested (GET)
    THEN check the response is valid
    """
    ##
    # Create booking 1
    ##
    # add client to queue first
    global payment_method_1
    payment_method_1 = PaymentMethods.query.filter_by(user_id=1).first()
    queue_data = {
                'profession_type': 'medical_doctor',
                'target_date': datetime.strptime(
                    telehealth_bookings_staff_4_client_1_data.get('target_date'), '%Y-%m-%d').isoformat(),
                'priority': False,
                'medical_gender': 'np',
                'location_id': 1,
                'payment_method_id': payment_method_1.idx
            }

    response = test_client.post('/telehealth/queue/client-pool/1/',
                                headers=client_auth_header, 
                                data=dumps(queue_data), 
                                content_type='application/json')


    response = test_client.post('/telehealth/bookings/?client_user_id={}&staff_user_id={}'.format(1,staff_users[0].user_id),
                                headers=client_auth_header, 
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
                'payment_method_id': payment_method_1.idx
            }

    response = test_client.post('/telehealth/queue/client-pool/1/',
                                headers=client_auth_header, 
                                data=dumps(queue_data), 
                                content_type='application/json')        
    
    response = test_client.post('/telehealth/bookings/?client_user_id={}&staff_user_id={}'.format(1,staff_users[0].user_id),
                                headers=client_auth_header, 
                                data=dumps(telehealth_bookings_staff_4_client_3_data), 
                                content_type='application/json')
                      
    assert response.status_code == 201            
    
    ##
    # Create booking 3
    ##
    
    # use different staff and client users. Must sign in as staff first
    client_4 = init_database.session.execute(
        select(User).
        where(User.email == 'test_remote_registration3@gmail.com')
    ).scalars().one_or_none()

     # sign in as client user 
    valid_credentials = base64.b64encode(
        f"{client_4.email}:{'password'}".encode(
            "utf-8")).decode("utf-8")
    
    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post('/client/token/',
                            headers=headers, 
                            content_type='application/json')
    token = response.json.get('token')
    client_4_auth_header = {'Authorization': f'Bearer {token}'}

    # add payment method to db
    test_client.post(f'/payment/methods/{client_4.user_id}/',
                                headers=client_4_auth_header,
                                data=dumps(payment_method_data['normal_data']),
                                content_type='application/json')
    payment_method = PaymentMethods.query.filter_by(user_id=client_4.user_id).first()

    # add client to queue first
    queue_data = {
                'profession_type': 'medical_doctor',
                'target_date': datetime.strptime(
                    telehealth_bookings_staff_8_client_5_data.get('target_date'), '%Y-%m-%d').isoformat(),
                'priority': False,
                'medical_gender': 'np',
                'location_id': 1,
                'payment_method_id': payment_method.idx
            }

    response = test_client.post(f'/telehealth/queue/client-pool/{client_4.user_id}/',
                                headers=client_4_auth_header, 
                                data=dumps(queue_data), 
                                content_type='application/json')

    response = test_client.post('/telehealth/bookings/?client_user_id={}&staff_user_id={}'.format(client_4.user_id,staff_users[2].user_id),
                                headers=client_4_auth_header, 
                                data=dumps(telehealth_bookings_staff_8_client_5_data), 
                                content_type='application/json')
    
    assert response.status_code == 201            

def test_generate_client_queue(test_client,init_database, client_auth_header,staff_auth_header):
    """
    GIVEN a api end point for client appointment queue
    WHEN the '/telehealth/queue/client-pool/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """   
    telehealth_queue_client_3_data['payment_method_id'] = payment_method_1.idx
    response = test_client.post('/telehealth/queue/client-pool/1/',
                                headers=client_auth_header, 
                                data=dumps(telehealth_queue_client_3_data), 
                                content_type='application/json')

    assert response.status_code == 201   

def test_client_time_select(test_client, init_database, client_auth_header):
    """
    GIVEN an api end point for looking client time select
    WHEN the  '/telehealth/client/time-select/<user_id>/' resource  is requested (GET)
    THEN check the response is valid
    """

    response = test_client.get('/telehealth/client/time-select/1/', headers=client_auth_header)

    assert response.status_code == 200
    assert response.json['total_options'] == 53


def test_full_system_with_settings(test_client, init_database, staff_auth_header, client_auth_header):
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
    current_availabilities = init_database.session.execute(
        delete(TelehealthStaffAvailability).
        where(TelehealthStaffAvailability.idx > 0)
    )
    ##
    # 1. Set staff's availability
    ##
    availability = {
                'settings': {
                'timezone': 'UTC',
                'auto_confirm': False
                },
                'availability' : [  {
                "day_of_week": "Wednesday",
                "start_time": "3:00:00",
                "end_time": "12:00:00"
                } 
            ]
        }
    response = test_client.post(f'/telehealth/settings/staff/availability/{2}/',
                                    headers=staff_auth_header, 
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
                    'payment_method_id': payment_method_1.idx
            }

    response = test_client.post('/telehealth/queue/client-pool/1/',
                                headers=client_auth_header, 
                                data=dumps(client_queue), 
                                content_type='application/json')


    ##
    # 3. Client requests to view availabilities for selected target date
    ##
    response = test_client.get('/telehealth/client/time-select/1/', headers=client_auth_header)

    assert response.status_code == 200
    assert response.json['appointment_times'][0]['start_time'] == '00:00:00'
    assert response.json['appointment_times'][0]['booking_window_id_start_time'] == 85
 
    assert response.json['appointment_times'][-1]['start_time'] == '04:30:00'
    assert response.json['appointment_times'][-1]['booking_window_id_start_time'] == 139
    assert response.json['total_options'] == 19

    ##
    # 4. Client selects an appointment time
    ##
    # select the booking that is at 4:30 Phx time/ 11:30 UTC  
    client_booking = {
            'target_date': '2024-11-6',
            'booking_window_id_start_time': response.json['appointment_times'][-1]['booking_window_id_start_time'],
            'booking_window_id_end_time': response.json['appointment_times'][-1]['booking_window_id_end_time'],
            'profession_type': 'medical_doctor'
        }

    response = test_client.post('/telehealth/bookings/?client_user_id={}&staff_user_id={}'.format(1,2),
                            headers=client_auth_header, 
                            data=dumps(client_booking), 
                            content_type='application/json')
    assert response.json['bookings'][0]['client_timezone'] == 'America/Phoenix'
    assert response.json['bookings'][0]['staff_timezone'] == 'UTC'
    assert response.json['bookings'][0]['status'] == 'Pending Staff Acceptance'
    assert response.json['bookings'][0]['payment_method_id'] == payment_method_1.idx

    booking_id = response.json['bookings'][0]['idx']

    ##
    # 4. Pull up bookings from the client and staff perspectives
    ##

    response = test_client.get('/telehealth/bookings/?client_user_id={}&staff_user_id={}'.format(1,2),
                        headers=staff_auth_header, 
                        data=dumps(client_booking), 
                        content_type='application/json')
    current_booking = (booking for booking in response.json['bookings'] if booking.booking_id == booking_id)
    for booking in response.json['bookings']:
        if booking['booking_id'] == booking_id:
            current_booking = booking
            break

    # booking time as seen by the staff
    assert current_booking['start_time'] == '11:30:00'
    assert current_booking['end_time'] == '11:50:00'
    assert current_booking['timezone'] == 'UTC'

    response = test_client.get('/telehealth/bookings/?client_user_id={}&staff_user_id={}'.format(1,2),
                        headers=client_auth_header, 
                        data=dumps(client_booking), 
                        content_type='application/json')
    
    for booking in response.json['bookings']:
        if booking['booking_id'] == booking_id:
            current_booking = booking
            break

    # booking time as seen by the client
    assert current_booking['start_time'] == '04:30:00'
    assert current_booking['end_time'] == '04:50:00'
    assert current_booking['timezone'] == 'America/Phoenix'


@pytest.mark.skip('This endpoint should no longer be used.')
def test_bookings_meeting_room_access(test_client,init_database,client_auth_header, staff_auth_header):
    user_id_arr = (1,2)
    for user_id in user_id_arr:
        user = init_database.session.execute(
            select(User).where(User.user_id == user_id)
        ).one_or_none()[0]
        # sign in as staff user 
        valid_credentials = base64.b64encode(
            f"{user.email}:{'password'}".encode(
                "utf-8")).decode("utf-8")
        
        headers = {'Authorization': f'Basic {valid_credentials}'}
        if user_id == 2:
            response = test_client.post('/staff/token/',
                                    headers=headers, 
                                    content_type='application/json')
        else:
            response = test_client.post('/client/token/',
                                    headers=headers, 
                                    content_type='application/json')            
        token = response.json.get('token')
        auth_header = {'Authorization': f'Bearer {token}'}
        response = test_client.get('/telehealth/bookings/meeting-room/access-token/1/', headers=auth_header)
        assert response.status_code == 200

def test_delete_generated_users(test_client, init_database, delete_users):
    assert 1 == 1