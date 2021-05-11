
import base64
from flask.json import dumps
import pytest
from sqlalchemy.sql.expression import select

# from tests.conftest import generate_users
from odyssey.api.user.models import User
from odyssey.api.telehealth.models import TelehealthStaffAvailability

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
    telehealth_queue_client_3_data
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

def test_generate_bookings(test_client, init_database, staff_auth_header):
    """
    GIVEN an api end point for looking client time select
    WHEN the  '/telehealth/bookings/' resource  is requested (GET)
    THEN check the response is valid
    """

    user = init_database.session.execute(
        select(User).where(User.user_id == staff_users[0].user_id)
    ).one_or_none()[0]
    # sign in as staff user 
    valid_credentials = base64.b64encode(
        f"{user.email}:{'password'}".encode(
            "utf-8")).decode("utf-8")
    
    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post('/staff/token/',
                            headers=headers, 
                            content_type='application/json')
    token = response.json.get('token')
    auth_header = {'Authorization': f'Bearer {token}'}

    response = test_client.post('/telehealth/bookings/?client_user_id={}&staff_user_id={}'.format(1,staff_users[0].user_id),
                                headers=auth_header, 
                                data=dumps(telehealth_bookings_staff_4_client_1_data), 
                                content_type='application/json')
                                
    assert response.status_code == 201            
    
    response = test_client.post('/telehealth/bookings/?client_user_id={}&staff_user_id={}'.format(1,staff_users[0].user_id),
                                headers=auth_header, 
                                data=dumps(telehealth_bookings_staff_4_client_3_data), 
                                content_type='application/json')
    assert response.status_code == 201            


    # use different staff and client users. Must sign in as staff first
    user = init_database.session.execute(
        select(User).where(User.user_id == staff_users[2].user_id)
    ).one_or_none()[0]
    # sign in as staff user 
    valid_credentials = base64.b64encode(
        f"{user.email}:{'password'}".encode(
            "utf-8")).decode("utf-8")
    
    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post('/staff/token/',
                            headers=headers, 
                            content_type='application/json')
    token = response.json.get('token')
    auth_header = {'Authorization': f'Bearer {token}'}
    
    client_4 = init_database.session.execute(
        select(User.user_id).
        where(User.email == 'test_remote_registration3@gmail.com')
    ).scalars().one_or_none()

    response = test_client.post('/telehealth/bookings/?client_user_id={}&staff_user_id={}'.format(client_4,staff_users[2].user_id),
                                headers=auth_header, 
                                data=dumps(telehealth_bookings_staff_8_client_5_data), 
                                content_type='application/json')
    
    assert response.status_code == 201            

def test_generate_client_queue(test_client,init_database, client_auth_header,staff_auth_header):
    """
    GIVEN a api end point for client appointment queue
    WHEN the '/telehealth/queue/client-pool/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """    
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