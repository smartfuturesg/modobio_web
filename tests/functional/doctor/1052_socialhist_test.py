
import time 

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.doctor.models import MedicalHistory 
from .data import (
    doctor_all_socialhistory_post_1_data, 
    doctor_all_socialhistory_post_2_data,
    doctor_all_socialhistory_break_post_1_data,
    doctor_all_socialhistory_break_post_2_data
)

# Test STD Look Up

def test_get_std_conditions(test_client, init_database, staff_auth_header):
    """
    GIVEN an api end point for looking up stored STDs
    WHEN the  '/doctor/lookupstd/' resource  is requested (GET)
    THEN check the response is valid
    """

    # send get request for client info on user_id = 1 
    response = test_client.get('/doctor/lookupstd/', headers=staff_auth_header)

    assert response.status_code == 200
    assert response.json['total_items'] == 22
    assert len(response.json['items']) == 22

def test_post_1_social_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for STD medical history assessment
    WHEN the '/doctor/medicalinfo/std/<user id>/' resource  is requested (POST)
    THEN check the response is valid
    """
    payload = doctor_all_socialhistory_post_1_data
    
    # send put request for client social history on user_id = 1 
    response = test_client.post('/doctor/medicalinfo/social/1/',
                                headers=client_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201
    # assert len(response.json['stds']) == 2

def test_get_social_medical_history(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for retrieving personal and family medical history
    WHEN the  '/doctor/medicalinfo/social/<user id>' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        # send get request for client family history on user_id = 1 
        response = test_client.get('/doctor/medicalinfo/social/1/',
                                    headers=header, 
                                    content_type='application/json')

        assert response.status_code == 200
        assert len(response.json['std_history']) == 3
        assert response.json['social_history']['currently_smoke'] == True

def test_post_2_social_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for STD medical history assessment
    WHEN the '/doctor/medicalinfo/std/<user id>/' resource  is requested (POST)
    THEN check the response is valid
    """
    payload = doctor_all_socialhistory_post_2_data
    
    # send put request for client social history on user_id = 1 
    response = test_client.post('/doctor/medicalinfo/social/1/',
                                headers=client_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201
    
def test_get_2_social_medical_history(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for retrieving personal and family medical history
    WHEN the  '/doctor/medicalinfo/social/<user id>' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        # send get request for client family history on user_id = 1 
        response = test_client.get('/doctor/medicalinfo/social/1/',
                                    headers=header, 
                                    content_type='application/json')

        assert response.status_code == 200
        assert len(response.json['std_history']) == 1
        assert response.json['social_history']['currently_smoke'] == False

def test_break_post_1_social_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for STD medical history assessment
    WHEN the '/doctor/medicalinfo/std/<user id>/' resource  is requested (POST)
    THEN check the response is valid
    """
    payload = doctor_all_socialhistory_break_post_1_data
    
    # send put request for client social history on user_id = 1 
    response = test_client.post('/doctor/medicalinfo/social/1/',
                                headers=client_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')

    # Currently smoke is false, and do not provide last_smoke (int)
    assert response.status_code == 405

def test_get_broke_1_social_medical_history(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for retrieving personal and family medical history
    WHEN the  '/doctor/medicalinfo/social/<user id>' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        # send get request for client family history on user_id = 1 
        response = test_client.get('/doctor/medicalinfo/social/1/',
                                    headers=header, 
                                    content_type='application/json')

        assert response.status_code == 200
        assert len(response.json['std_history']) == 1
        assert response.json['social_history']['currently_smoke'] == False

def test_break_post_2_social_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for STD medical history assessment
    WHEN the '/doctor/medicalinfo/std/<user id>/' resource  is requested (POST)
    THEN check the response is valid
    """
    payload = doctor_all_socialhistory_break_post_2_data
    
    # send put request for client social history on user_id = 1 
    response = test_client.post('/doctor/medicalinfo/social/1/',
                                headers=client_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')
    # STD lookup out of range
    assert response.status_code == 405

def test_get_broke_2_social_medical_history(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for retrieving personal and family medical history
    WHEN the  '/doctor/medicalinfo/social/<user id>' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        # send get request for client family history on user_id = 1 
        response = test_client.get('/doctor/medicalinfo/social/1/',
                                    headers=header, 
                                    content_type='application/json')

        assert response.status_code == 200
        assert len(response.json['std_history']) == 1
        assert response.json['social_history']['currently_smoke'] == False        

    