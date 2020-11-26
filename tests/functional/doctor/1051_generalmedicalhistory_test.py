
import time 

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.doctor.models import MedicalHistory 
from .data import (
    doctor_medicalgeneralinfo_post_data,
    doctor_medicalgeneralinfo_put_data,
    doctor_medicalmedicationsinfo_post_data,
    doctor_medicalmedicationsinfo_put_data,
    doctor_medicalallergiesinfo_post_data,
    doctor_medicalallergiesinfo_put_data
)

def test_post_general_medical_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for general medical history assessment
    WHEN the '/doctor/medicalinfo/general/<user_id>' resource  is requested (POST)
    By a logged-in CLIENT
    THEN check the response is valid
    """
   
    payload = doctor_medicalgeneralinfo_post_data
    
    # send post request for client general medical history on user_id = 1 
    response = test_client.post('/doctor/medicalinfo/general/1/',
                                headers=client_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 201 
    assert response.json['primary_doctor_contact_name'] == 'Dr Guy'


def test_put_general_medical_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for general medical history assessment
    WHEN the '/doctor/medicalinfo/general/<user id>/' resource  is requested (PUT)
    THEN check the response is valid
    """
    payload = doctor_medicalgeneralinfo_put_data
    
    # send put request for client general medical history on user_id = 1 
    response = test_client.put('/doctor/medicalinfo/general/1/',
                                headers=client_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201
    assert response.json['primary_doctor_contact_name'] == 'Dr Steve'

def test_get_general_medical_history(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for retrieving general medical history
    WHEN the  '/doctor/medicalinfo/general/<user id>' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        # send get request for client general medical history on user_id = 1 
        response = test_client.get('/doctor/medicalinfo/general/1/',
                                    headers=header, 
                                    content_type='application/json')
                                    
        assert response.status_code == 200
        assert response.json['primary_doctor_contact_name'] == 'Dr Steve'      

################ TEST MEDICATION HISTORY ####################

def test_post_medication_medical_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for medication history assessment
    WHEN the '/doctor/medicalinfo/medications/<user_id>' resource  is requested (POST)
    By a logged-in CLIENT
    THEN check the response is valid
    """
   
    payload = doctor_medicalmedicationsinfo_post_data
    
    # send post request for client medication history on user_id = 1 
    response = test_client.post('/doctor/medicalinfo/medications/1/',
                                headers=client_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 201 
    assert response.json['medications'][0]['medication_name'] == 'medName1'
    assert len(response.json['medications']) == 2

def test_put_medication_medical_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for medication history assessment
    WHEN the '/doctor/medicalgeneralinfo/<user id>/' resource  is requested (PUT)
    THEN check the response is valid
    """
    payload = doctor_medicalmedicationsinfo_put_data
    
    # send put request for client medication history on user_id = 1 
    response = test_client.put('/doctor/medicalinfo/medications/1/',
                                headers=client_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201
    assert response.json['medications'][0]['medication_name'] == 'medName4'
    assert len(response.json['medications']) == 2

def test_get_medication_medical_history(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for retrieving medication history
    WHEN the  '/doctor/medicalgeneralinfo/<user id>' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        # send get request for client medication history on user_id = 1 
        response = test_client.get('/doctor/medicalinfo/medications/1/',
                                    headers=header, 
                                    content_type='application/json')
                                    
        assert response.status_code == 200
        assert response.json['medications'][0]['medication_name'] == 'medName1'
        assert len(response.json['medications']) == 3

################ TEST ALLERGY HISTORY ####################

def test_post_allergy_medical_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for allergy medical history assessment
    WHEN the '/doctor/medicalinfo/allergies/<user_id>' resource  is requested (POST)
    By a logged-in CLIENT
    THEN check the response is valid
    """
   
    payload = doctor_medicalallergiesinfo_post_data
    
    # send post request for client medication allergy history on user_id = 1 
    response = test_client.post('/doctor/medicalinfo/allergies/1/',
                                headers=client_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 201 
    assert response.json['allergies'][0]['medication_name'] == 'medName3'
    assert len(response.json['allergies']) == 2

def test_put_allergy_medical_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for allergy medical history assessment
    WHEN the '/doctor/medicalgeneralinfo/<user id>/' resource  is requested (PUT)
    THEN check the response is valid
    """
    payload = doctor_medicalallergiesinfo_put_data
    
    # send put request for client medication allergy history on user_id = 1 
    response = test_client.put('/doctor/medicalinfo/allergies/1/',
                                headers=client_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201
    assert response.json['allergies'][0]['medication_name'] == 'medName3'
    assert len(response.json['allergies']) == 2


def test_get_allergy_medical_history(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for retrieving allergy medical history
    WHEN the  '/doctor/medicalgeneralinfo/<user id>' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        # send get request for client medication allergy history on user_id = 1 
        response = test_client.get('/doctor/medicalinfo/allergies/1/',
                                    headers=header, 
                                    content_type='application/json')
                                    
        assert response.status_code == 200
        assert response.json['allergies'][0]['medication_name'] == 'medName3'
        assert len(response.json['allergies']) == 3  