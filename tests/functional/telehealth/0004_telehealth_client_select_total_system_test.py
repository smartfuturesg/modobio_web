
from flask.json import dumps

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

def test_generate_staff_availability(test_client, init_database, generate_users, staff_auth_header):
    """
    GIVEN an api end point for looking client time select
    WHEN the  '/telehealth/client/time-select/<user_id>/' resource  is requested (GET)
    THEN check the response is valid
    """

    # GENERATE STAFF AVAILABILITY
    response = test_client.post('/telehealth/settings/staff/availability/9/',
                                headers=staff_auth_header, 
                                data=dumps(telehealth_staff_4_general_availability_post_data), 
                                content_type='application/json')
    response = test_client.post('/telehealth/settings/staff/availability/11/',
                                headers=staff_auth_header, 
                                data=dumps(telehealth_staff_6_general_availability_post_data), 
                                content_type='application/json')
    response = test_client.post('/telehealth/settings/staff/availability/13/',
                                headers=staff_auth_header, 
                                data=dumps(telehealth_staff_8_general_availability_post_data), 
                                content_type='application/json')
    response = test_client.post('/telehealth/settings/staff/availability/15/',
                                headers=staff_auth_header, 
                                data=dumps(telehealth_staff_10_general_availability_post_data), 
                                content_type='application/json')
    response = test_client.post('/telehealth/settings/staff/availability/17/',
                                headers=staff_auth_header, 
                                data=dumps(telehealth_staff_12_general_availability_post_data), 
                                content_type='application/json')
    response = test_client.post('/telehealth/settings/staff/availability/19/',
                                headers=staff_auth_header, 
                                data=dumps(telehealth_staff_14_general_availability_post_data), 
                                content_type='application/json')    

    assert response.status_code == 201

def test_generate_bookings(test_client, init_database, staff_auth_header):
    response = test_client.post('/telehealth/bookings/?client_user_id={}&staff_user_id={}'.format(1,9),
                                headers=staff_auth_header, 
                                data=dumps(telehealth_bookings_staff_4_client_1_data), 
                                content_type='application/json')

    response = test_client.post('/telehealth/bookings/?client_user_id={}&staff_user_id={}'.format(1,9),
                                headers=staff_auth_header, 
                                data=dumps(telehealth_bookings_staff_4_client_3_data), 
                                content_type='application/json')

    response = test_client.post('/telehealth/bookings/?client_user_id={}&staff_user_id={}'.format(4,13),
                                headers=staff_auth_header, 
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

    assert response.status_code == 200   

def test_client_time_select(test_client, init_database, staff_auth_header):
    """
    GIVEN an api end point for looking client time select
    WHEN the  '/telehealth/client/time-select/<user_id>/' resource  is requested (GET)
    THEN check the response is valid
    """

    response = test_client.get('/telehealth/client/time-select/1/', headers=staff_auth_header)

    assert response.status_code == 201
    assert response.json['total_options'] == 59
    

def test_delete_generated_users(test_client, init_database, delete_users):
    assert 1 == 1