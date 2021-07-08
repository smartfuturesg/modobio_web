
import time 

from flask.json import dumps
from odyssey.api.staff.models import StaffRoles
from odyssey.api.payment.models import PaymentMethods

from .data import (
    telehealth_staff_general_availability_1_post_data,
    telehealth_staff_general_availability_2_post_data,
    telehealth_staff_general_availability_3_post_data,
    telehealth_staff_general_availability_bad_3_post_data,
    telehealth_staff_general_availability_bad_4_post_data,
    telehealth_staff_general_availability_bad_5_post_data,
    telehealth_staff_general_availability_bad_6_post_data,
    telehealth_staff_general_availability_bad_7_post_data,
    telehealth_queue_client_pool_8_post_data    
)

def test_post_1_staff_general_availability(test_client, init_database,client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # Add Staff Operational Territories to staff with user_id 2 and only for medical_doctor role
    role = StaffRoles.query.filter_by(user_id = 2, role = 'medical_doctor').one_or_none()
    payload = {'operational_territories': [{ 'role_id': role.idx,'operational_territory_id': 1}]}
    test_client.post(f'/staff/operational-territories/2/', headers=staff_auth_header, data=dumps(payload), content_type='application/json')

    response = test_client.post('/telehealth/settings/staff/availability/2/',
                                headers=staff_auth_header, 
                                data=dumps(telehealth_staff_general_availability_1_post_data), 
                                content_type='application/json')
    assert response.status_code == 201

    payment_method = PaymentMethods.query.filter_by(user_id=1).first()
    telehealth_queue_client_pool_8_post_data['payment_method_id'] = payment_method.idx

    response = test_client.post('/telehealth/queue/client-pool/1/',
                                headers=client_auth_header, 
                                data=dumps(telehealth_queue_client_pool_8_post_data), 
                                content_type='application/json')
    # This get request was inserted here to show that there needs to be at least 10 
    # valid times returned. If there are less than 10 appointment times, then we increment onward a day
    # and keep going until the 10 times is valid
    response = test_client.get('/telehealth/client/time-select/1/', headers=client_auth_header)

    assert response.json['appointment_times'][0]['target_date'] == '2022-04-04'
    assert response.json['appointment_times'][1]['target_date'] == '2022-04-04'
    assert response.json['appointment_times'][2]['target_date'] == '2022-04-04'
    assert response.json['appointment_times'][3]['target_date'] == '2022-04-11'
    assert response.json['appointment_times'][6]['target_date'] == '2022-04-18'
    assert response.json['appointment_times'][9]['target_date'] == '2022-04-25'
    assert response.json['total_options'] == 12

    # 3_midnight_bug_staff_general_availability
    response = test_client.post('/telehealth/settings/staff/availability/2/',
                                headers=staff_auth_header, 
                                data=dumps(telehealth_staff_general_availability_3_post_data), 
                                content_type='application/json')
    assert response.status_code == 201

def test_get_3_staff_availability(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/<user_id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/telehealth/settings/staff/availability/2/',
                                headers=staff_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200
    assert [response.json['availability'][0]['day_of_week'], response.json['availability'][0]['start_time'], response.json['availability'][0]['end_time']] == ['Monday', '00:00:00', '12:00:00'] 

    response = test_client.get('/telehealth/settings/staff/availability/2/',
                            headers=staff_auth_header, 
                            content_type='application/json')
    assert response.status_code == 200

def test_post_2_staff_general_availability(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.post('/telehealth/settings/staff/availability/2/',
                                headers=staff_auth_header, 
                                data=dumps(telehealth_staff_general_availability_2_post_data), 
                                content_type='application/json')

    assert response.status_code == 201


def test_get_2_staff_availability(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/<user_id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/telehealth/settings/staff/availability/2/',
                                headers=staff_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200
    assert [response.json['availability'][0]['day_of_week'], response.json['availability'][0]['start_time'], response.json['availability'][0]['end_time']] == ['Monday', '08:00:00', '09:00:00'] 
    assert [response.json['availability'][1]['day_of_week'], response.json['availability'][1]['start_time'], response.json['availability'][1]['end_time']] == ['Monday', '13:00:00', '20:00:00'] 
    assert [response.json['availability'][2]['day_of_week'], response.json['availability'][2]['start_time'], response.json['availability'][2]['end_time']] == ['Tuesday', '11:00:00', '13:00:00'] 
    assert [response.json['availability'][3]['day_of_week'], response.json['availability'][3]['start_time'], response.json['availability'][3]['end_time']] == ['Wednesday', '09:00:00', '20:00:00'] 
    assert [response.json['availability'][4]['day_of_week'], response.json['availability'][4]['start_time'], response.json['availability'][4]['end_time']] == ['Friday', '13:00:00', '20:00:00'] 
    assert [response.json['availability'][5]['day_of_week'], response.json['availability'][5]['start_time'], response.json['availability'][5]['end_time']] == ['Saturday', '13:00:00', '20:00:00'] 
    assert [response.json['availability'][6]['day_of_week'], response.json['availability'][6]['start_time'], response.json['availability'][6]['end_time']] == ['Sunday', '13:00:00', '20:00:00'] 


def test_invalid_post_3_staff_general_availability(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.post('/telehealth/settings/staff/availability/2/',
                                headers=staff_auth_header, 
                                data=dumps(telehealth_staff_general_availability_bad_3_post_data), 
                                content_type='application/json')
    assert response.status_code == 400


def test_get_3_staff_availability(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/<user_id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/telehealth/settings/staff/availability/2/',
                                headers=staff_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200
    assert [response.json['availability'][0]['day_of_week'], response.json['availability'][0]['start_time'], response.json['availability'][0]['end_time']] == ['Monday', '08:00:00', '09:00:00'] 
    assert [response.json['availability'][1]['day_of_week'], response.json['availability'][1]['start_time'], response.json['availability'][1]['end_time']] == ['Monday', '13:00:00', '20:00:00'] 
    assert [response.json['availability'][2]['day_of_week'], response.json['availability'][2]['start_time'], response.json['availability'][2]['end_time']] == ['Tuesday', '11:00:00', '13:00:00'] 
    assert [response.json['availability'][3]['day_of_week'], response.json['availability'][3]['start_time'], response.json['availability'][3]['end_time']] == ['Wednesday', '09:00:00', '20:00:00'] 
    assert [response.json['availability'][4]['day_of_week'], response.json['availability'][4]['start_time'], response.json['availability'][4]['end_time']] == ['Friday', '13:00:00', '20:00:00'] 
    assert [response.json['availability'][5]['day_of_week'], response.json['availability'][5]['start_time'], response.json['availability'][5]['end_time']] == ['Saturday', '13:00:00', '20:00:00'] 
    assert [response.json['availability'][6]['day_of_week'], response.json['availability'][6]['start_time'], response.json['availability'][6]['end_time']] == ['Sunday', '13:00:00', '20:00:00'] 

def test_invalid_post_4_staff_general_availability(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.post('/telehealth/settings/staff/availability/2/',
                                headers=staff_auth_header, 
                                data=dumps(telehealth_staff_general_availability_bad_4_post_data), 
                                content_type='application/json')
    assert response.status_code == 400


def test_get_4_staff_availability(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/<user_id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/telehealth/settings/staff/availability/2/',
                                headers=staff_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200
    assert [response.json['availability'][0]['day_of_week'], response.json['availability'][0]['start_time'], response.json['availability'][0]['end_time']] == ['Monday', '08:00:00', '09:00:00'] 
    assert [response.json['availability'][1]['day_of_week'], response.json['availability'][1]['start_time'], response.json['availability'][1]['end_time']] == ['Monday', '13:00:00', '20:00:00'] 
    assert [response.json['availability'][2]['day_of_week'], response.json['availability'][2]['start_time'], response.json['availability'][2]['end_time']] == ['Tuesday', '11:00:00', '13:00:00'] 
    assert [response.json['availability'][3]['day_of_week'], response.json['availability'][3]['start_time'], response.json['availability'][3]['end_time']] == ['Wednesday', '09:00:00', '20:00:00'] 
    assert [response.json['availability'][4]['day_of_week'], response.json['availability'][4]['start_time'], response.json['availability'][4]['end_time']] == ['Friday', '13:00:00', '20:00:00'] 
    assert [response.json['availability'][5]['day_of_week'], response.json['availability'][5]['start_time'], response.json['availability'][5]['end_time']] == ['Saturday', '13:00:00', '20:00:00'] 
    assert [response.json['availability'][6]['day_of_week'], response.json['availability'][6]['start_time'], response.json['availability'][6]['end_time']] == ['Sunday', '13:00:00', '20:00:00'] 

def test_invalid_post_5_staff_general_availability(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.post('/telehealth/settings/staff/availability/2/',
                                headers=staff_auth_header, 
                                data=dumps(telehealth_staff_general_availability_bad_5_post_data), 
                                content_type='application/json')
    assert response.status_code == 400


def test_get_5_staff_availability(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/<user_id>/' resource  is requested (GET)
    THEN check the response is valid
    """
   
    response = test_client.get('/telehealth/settings/staff/availability/2/',
                                headers=staff_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200   
    assert [response.json['availability'][0]['day_of_week'], response.json['availability'][0]['start_time'], response.json['availability'][0]['end_time']] == ['Monday', '08:00:00', '09:00:00'] 
    assert [response.json['availability'][1]['day_of_week'], response.json['availability'][1]['start_time'], response.json['availability'][1]['end_time']] == ['Monday', '13:00:00', '20:00:00'] 
    assert [response.json['availability'][2]['day_of_week'], response.json['availability'][2]['start_time'], response.json['availability'][2]['end_time']] == ['Tuesday', '11:00:00', '13:00:00'] 
    assert [response.json['availability'][3]['day_of_week'], response.json['availability'][3]['start_time'], response.json['availability'][3]['end_time']] == ['Wednesday', '09:00:00', '20:00:00'] 
    assert [response.json['availability'][4]['day_of_week'], response.json['availability'][4]['start_time'], response.json['availability'][4]['end_time']] == ['Friday', '13:00:00', '20:00:00'] 
    assert [response.json['availability'][5]['day_of_week'], response.json['availability'][5]['start_time'], response.json['availability'][5]['end_time']] == ['Saturday', '13:00:00', '20:00:00'] 
    assert [response.json['availability'][6]['day_of_week'], response.json['availability'][6]['start_time'], response.json['availability'][6]['end_time']] == ['Sunday', '13:00:00', '20:00:00'] 

def test_invalid_post_6_staff_general_availability(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.post('/telehealth/settings/staff/availability/2/',
                                headers=staff_auth_header, 
                                data=dumps(telehealth_staff_general_availability_bad_6_post_data), 
                                content_type='application/json')
    assert response.status_code == 400


def test_get_6_staff_availability(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/<user_id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/telehealth/settings/staff/availability/2/',
                                headers=staff_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200 
    assert [response.json['availability'][0]['day_of_week'], response.json['availability'][0]['start_time'], response.json['availability'][0]['end_time']] == ['Monday', '08:00:00', '09:00:00'] 
    assert [response.json['availability'][1]['day_of_week'], response.json['availability'][1]['start_time'], response.json['availability'][1]['end_time']] == ['Monday', '13:00:00', '20:00:00'] 
    assert [response.json['availability'][2]['day_of_week'], response.json['availability'][2]['start_time'], response.json['availability'][2]['end_time']] == ['Tuesday', '11:00:00', '13:00:00'] 
    assert [response.json['availability'][3]['day_of_week'], response.json['availability'][3]['start_time'], response.json['availability'][3]['end_time']] == ['Wednesday', '09:00:00', '20:00:00'] 
    assert [response.json['availability'][4]['day_of_week'], response.json['availability'][4]['start_time'], response.json['availability'][4]['end_time']] == ['Friday', '13:00:00', '20:00:00'] 
    assert [response.json['availability'][5]['day_of_week'], response.json['availability'][5]['start_time'], response.json['availability'][5]['end_time']] == ['Saturday', '13:00:00', '20:00:00'] 
    assert [response.json['availability'][6]['day_of_week'], response.json['availability'][6]['start_time'], response.json['availability'][6]['end_time']] == ['Sunday', '13:00:00', '20:00:00']         

def test_invalid_post_7_staff_general_availability(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.post('/telehealth/settings/staff/availability/2/',
                                headers=staff_auth_header, 
                                data=dumps(telehealth_staff_general_availability_bad_7_post_data), 
                                content_type='application/json')
    assert response.status_code == 405


def test_get_7_staff_availability(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/<user_id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/telehealth/settings/staff/availability/2/',
                                headers=staff_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200   
    assert [response.json['availability'][0]['day_of_week'], response.json['availability'][0]['start_time'], response.json['availability'][0]['end_time']] == ['Monday', '08:00:00', '09:00:00'] 
    assert [response.json['availability'][1]['day_of_week'], response.json['availability'][1]['start_time'], response.json['availability'][1]['end_time']] == ['Monday', '13:00:00', '20:00:00'] 
    assert [response.json['availability'][2]['day_of_week'], response.json['availability'][2]['start_time'], response.json['availability'][2]['end_time']] == ['Tuesday', '11:00:00', '13:00:00'] 
    assert [response.json['availability'][3]['day_of_week'], response.json['availability'][3]['start_time'], response.json['availability'][3]['end_time']] == ['Wednesday', '09:00:00', '20:00:00'] 
    assert [response.json['availability'][4]['day_of_week'], response.json['availability'][4]['start_time'], response.json['availability'][4]['end_time']] == ['Friday', '13:00:00', '20:00:00'] 
    assert [response.json['availability'][5]['day_of_week'], response.json['availability'][5]['start_time'], response.json['availability'][5]['end_time']] == ['Saturday', '13:00:00', '20:00:00'] 
    assert [response.json['availability'][6]['day_of_week'], response.json['availability'][6]['start_time'], response.json['availability'][6]['end_time']] == ['Sunday', '13:00:00', '20:00:00']                 

     

    