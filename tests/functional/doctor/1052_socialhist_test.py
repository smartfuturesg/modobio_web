
import time 

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.doctor.models import MedicalHistory 
from .data import doctor_socialhist_post_data, doctor_socialhist_put_data, doctor_std_put_1_data, doctor_std_put_2_data

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

def test_put_1_std_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for STD medical history assessment
    WHEN the '/doctor/medicalinfo/std/<user id>/' resource  is requested (PUT)
    THEN check the response is valid
    """
    payload = doctor_std_put_1_data
    
    # send put request for client social history on user_id = 1 
    response = test_client.put('/doctor/medicalinfo/std/1/',
                                headers=client_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201
    assert len(response.json['stds']) == 2

def test_post_social_medical_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for medical history assessment
    WHEN the '/doctor/medicalinfo/social/<user_id>' resource  is requested (POST)
    By a logged-in CLIENT
    THEN check the response is valid
    """
    payload = doctor_socialhist_post_data

    # send post request for client social history on user_id = 1 
    response = test_client.post('/doctor/medicalinfo/social/1/',
                                headers=client_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 201
    assert response.json['currently_smoke'] == False
    assert response.json['last_smoke'] == 5

def test_put_social_medical_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for social medical history assessment
    WHEN the '/doctor/medicalinfo/social/<user id>/' resource  is requested (PUT)
    THEN check the response is valid
    """
    payload = doctor_socialhist_put_data
    
    # send put request for client social history on user_id = 1 
    response = test_client.put('/doctor/medicalinfo/social/1/',
                                headers=client_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201
    assert response.json['currently_smoke'] == True
    assert response.json['avg_num_cigs'] == 5
    assert response.json['last_smoke'] == None

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
        assert response.json['social_history']['currently_smoke'] == True
        assert len(response.json['std_history']) == 2

def test_put_2_std_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for STD medical history assessment
    WHEN the '/doctor/medicalinfo/std/<user id>/' resource  is requested (PUT)
    THEN check the response is valid
    """
    payload = doctor_std_put_2_data
    
    # send put request for client social history on user_id = 1 
    response = test_client.put('/doctor/medicalinfo/std/1/',
                                headers=client_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201
    assert len(response.json['stds']) == 2

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
        assert response.json['social_history']['currently_smoke'] == True
        assert len(response.json['std_history']) == 2  
        assert response.json['std_history'][-1]['std_id'] == 3