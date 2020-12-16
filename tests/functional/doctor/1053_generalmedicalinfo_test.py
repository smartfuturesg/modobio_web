
import time 

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.doctor.models import MedicalHistory 
from .data import (
    doctor_all_generalmedicalinfo_post_1_data,
    doctor_all_generalmedicalinfo_post_2_data
)

def test_post_1_general_medical_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for general medical history assessment
    WHEN the '/doctor/medicalinfo/general/<user_id>' resource  is requested (POST)
    By a logged-in CLIENT
    THEN check the response is valid
    """
   
    payload = doctor_all_generalmedicalinfo_post_1_data
    
    # send post request for client general medical history on user_id = 1 
    response = test_client.post('/doctor/medicalgeneralinfo/1/',
                                headers=client_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 201 
    # assert response.json['primary_doctor_contact_name'] == 'Dr Guy'

def test_get_1_general_medical_history(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for retrieving general medical history
    WHEN the  '/doctor/medicalinfo/general/<user id>' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        # send get request for client general medical history on user_id = 1 
        response = test_client.get('/doctor/medicalgeneralinfo/1/',
                                    headers=header, 
                                    content_type='application/json')
                                    
        assert response.status_code == 200
        assert response.json['gen_info']['primary_doctor_contact_name'] == 'Dr Guy'
        assert len(response.json['medications']) == 2
        assert len(response.json['allergies']) == 3

def test_post_2_general_medical_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for general medical history assessment
    WHEN the '/doctor/medicalinfo/general/<user_id>' resource  is requested (POST)
    By a logged-in CLIENT
    THEN check the response is valid
    """
   
    payload = doctor_all_generalmedicalinfo_post_2_data
    
    # send post request for client general medical history on user_id = 1 
    response = test_client.post('/doctor/medicalgeneralinfo/1/',
                                headers=client_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 201 
    # assert response.json['primary_doctor_contact_name'] == 'Dr Guy'

def test_get_2_general_medical_history(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for retrieving general medical history
    WHEN the  '/doctor/medicalinfo/general/<user id>' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        # send get request for client general medical history on user_id = 1 
        response = test_client.get('/doctor/medicalgeneralinfo/1/',
                                    headers=header, 
                                    content_type='application/json')
                                    
        assert response.status_code == 200
        assert response.json['gen_info']['primary_doctor_contact_name'] == 'Dr Steve'
        assert len(response.json['medications']) == 3
        assert len(response.json['allergies']) == 1