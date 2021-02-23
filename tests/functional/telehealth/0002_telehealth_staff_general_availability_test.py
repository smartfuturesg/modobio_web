
import time 

from flask.json import dumps

from .data import (
    telehealth_staff_general_availability_1_post_data,
    telehealth_staff_general_availability_2_post_data
)

def test_post_1_staff_general_availability(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.post('/telehealth/settings/staff/availability/1/',
                                headers=client_auth_header, 
                                data=dumps(telehealth_staff_general_availability_1_post_data), 
                                content_type='application/json')

    assert response.status_code == 200


def test_get_1_specific_client_appointment_queue(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/<user_id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        response = test_client.get('/telehealth/settings/staff/availability/1/',
                                    headers=header, 
                                    content_type='application/json')
        
        assert response.status_code == 200

def test_post_2_staff_general_availability(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.post('/telehealth/settings/staff/availability/1/',
                                headers=client_auth_header, 
                                data=dumps(telehealth_staff_general_availability_2_post_data), 
                                content_type='application/json')

    assert response.status_code == 200


def test_get_2_specific_client_appointment_queue(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for staff general availability
    WHEN the '/telehealth/settings/staff/availability/<user_id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        response = test_client.get('/telehealth/settings/staff/availability/1/',
                                    headers=header, 
                                    content_type='application/json')
        
        assert response.status_code == 200
