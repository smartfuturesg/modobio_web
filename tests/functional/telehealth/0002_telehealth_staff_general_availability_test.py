
import time 

from flask.json import dumps

from .data import (
    telehealth_staff_general_availability_1_post_data,
    telehealth_staff_general_availability_2_post_data,
    telehealth_staff_general_availability_3_post_data,
    telehealth_staff_general_availability_bad_3_post_data,
    telehealth_staff_general_availability_bad_4_post_data,
    telehealth_staff_general_availability_bad_5_post_data,
    telehealth_staff_general_availability_bad_6_post_data,
    telehealth_staff_general_availability_bad_7_post_data
)

def test_post_1_staff_general_availability(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.post('/telehealth/settings/staff/availability/2/',
                                headers=staff_auth_header, 
                                data=dumps(telehealth_staff_general_availability_1_post_data), 
                                content_type='application/json')

    assert response.status_code == 201
    


def test_get_1_staff_availability(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/<user_id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, ):
        response = test_client.get('/telehealth/settings/staff/availability/2/',
                                    headers=header, 
                                    content_type='application/json')
        
        assert response.status_code == 201

def test_post_3_midnight_bug_staff_general_availability(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
   
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
    for header in (staff_auth_header, ):
        response = test_client.get('/telehealth/settings/staff/availability/2/',
                                    headers=header, 
                                    content_type='application/json')
        
        assert response.status_code == 201
        assert [response.json['availability'][0]['day_of_week'], response.json['availability'][0]['start_time'], response.json['availability'][0]['end_time']] == ['Monday', '00:00:00', '12:00:00'] 

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
    for header in (staff_auth_header, ):
        response = test_client.get('/telehealth/settings/staff/availability/2/',
                                    headers=header, 
                                    content_type='application/json')
        
        assert response.status_code == 201
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


def test_get_3_staff_availability(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/<user_id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, ):
        response = test_client.get('/telehealth/settings/staff/availability/2/',
                                    headers=header, 
                                    content_type='application/json')
        
        assert response.status_code == 201
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


def test_get_4_staff_availability(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/<user_id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, ):
        response = test_client.get('/telehealth/settings/staff/availability/2/',
                                    headers=header, 
                                    content_type='application/json')
        
        assert response.status_code == 201
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


def test_get_5_staff_availability(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/<user_id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, ):
        response = test_client.get('/telehealth/settings/staff/availability/2/',
                                    headers=header, 
                                    content_type='application/json')
        
        assert response.status_code == 201   
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


def test_get_6_staff_availability(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/<user_id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, ):
        response = test_client.get('/telehealth/settings/staff/availability/2/',
                                    headers=header, 
                                    content_type='application/json')
        
        assert response.status_code == 201 
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


def test_get_7_staff_availability(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/<user_id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, ):
        response = test_client.get('/telehealth/settings/staff/availability/2/',
                                    headers=header, 
                                    content_type='application/json')
        
        assert response.status_code == 201   
        assert [response.json['availability'][0]['day_of_week'], response.json['availability'][0]['start_time'], response.json['availability'][0]['end_time']] == ['Monday', '08:00:00', '09:00:00'] 
        assert [response.json['availability'][1]['day_of_week'], response.json['availability'][1]['start_time'], response.json['availability'][1]['end_time']] == ['Monday', '13:00:00', '20:00:00'] 
        assert [response.json['availability'][2]['day_of_week'], response.json['availability'][2]['start_time'], response.json['availability'][2]['end_time']] == ['Tuesday', '11:00:00', '13:00:00'] 
        assert [response.json['availability'][3]['day_of_week'], response.json['availability'][3]['start_time'], response.json['availability'][3]['end_time']] == ['Wednesday', '09:00:00', '20:00:00'] 
        assert [response.json['availability'][4]['day_of_week'], response.json['availability'][4]['start_time'], response.json['availability'][4]['end_time']] == ['Friday', '13:00:00', '20:00:00'] 
        assert [response.json['availability'][5]['day_of_week'], response.json['availability'][5]['start_time'], response.json['availability'][5]['end_time']] == ['Saturday', '13:00:00', '20:00:00'] 
        assert [response.json['availability'][6]['day_of_week'], response.json['availability'][6]['start_time'], response.json['availability'][6]['end_time']] == ['Sunday', '13:00:00', '20:00:00']                 

     

    