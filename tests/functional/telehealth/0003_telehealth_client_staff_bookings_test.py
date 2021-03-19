
import time 

from flask.json import dumps

from .data import (
    telehealth_client_staff_bookings_post_1_data,
    telehealth_client_staff_bookings_post_2_data,
    telehealth_client_staff_bookings_post_3_data,
    telehealth_client_staff_bookings_post_4_data,
    telehealth_client_staff_bookings_post_5_data,
    telehealth_client_staff_bookings_post_6_data

)

def test_post_1_client_staff_bookings(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for client staff bookings
    WHEN the '/telehealth/bookings/<int:client_user_id>/<int:staff_user_id>/' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.post('/telehealth/bookings/1/2/',
                                headers=staff_auth_header, 
                                data=dumps(telehealth_client_staff_bookings_post_1_data), 
                                content_type='application/json')
    assert response.status_code == 201

def test_post_2_client_staff_bookings(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for client staff bookings
    WHEN the '/telehealth/bookings/<int:client_user_id>/<int:staff_user_id>/' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.post('/telehealth/bookings/1/2/',
                                headers=staff_auth_header, 
                                data=dumps(telehealth_client_staff_bookings_post_2_data), 
                                content_type='application/json')
    assert response.status_code == 201    

def test_post_3_client_staff_bookings(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for client staff bookings
    WHEN the '/telehealth/bookings/<int:client_user_id>/<int:staff_user_id>/' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.post('/telehealth/bookings/1/2/',
                                headers=staff_auth_header, 
                                data=dumps(telehealth_client_staff_bookings_post_3_data), 
                                content_type='application/json')
    assert response.status_code == 405   

def test_post_4_client_staff_bookings(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for client staff bookings
    WHEN the '/telehealth/bookings/<int:client_user_id>/<int:staff_user_id>/' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.post('/telehealth/bookings/1/2/',
                                headers=staff_auth_header, 
                                data=dumps(telehealth_client_staff_bookings_post_3_data), 
                                content_type='application/json')
    assert response.status_code == 405

def test_post_5_client_staff_bookings(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for client staff bookings
    WHEN the '/telehealth/bookings/<int:client_user_id>/<int:staff_user_id>/' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.post('/telehealth/bookings/1/2/',
                                headers=staff_auth_header, 
                                data=dumps(telehealth_client_staff_bookings_post_3_data), 
                                content_type='application/json')
    assert response.status_code == 405        

def test_post_6_client_staff_bookings(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for client staff bookings
    WHEN the '/telehealth/bookings/<int:client_user_id>/<int:staff_user_id>/' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.post('/telehealth/bookings/1/2/',
                                headers=staff_auth_header, 
                                data=dumps(telehealth_client_staff_bookings_post_3_data), 
                                content_type='application/json')
    assert response.status_code == 405

def test_get_1_staff_bookings(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for staff bookings
    WHEN the '/telehealth/bookings/staff/<int:staff_user_id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/telehealth/bookings/staff/2/',
                                headers=staff_auth_header, 
                                content_type='application/json')
                                
    assert response.status_code == 201
    
def test_get_2_client_bookings(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for client bookings
    WHEN the '/telehealth/bookings/client/<int:client_user_id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/telehealth/bookings/client/1/',
                                headers=staff_auth_header, 
                                content_type='application/json')
                                
    assert response.status_code == 201