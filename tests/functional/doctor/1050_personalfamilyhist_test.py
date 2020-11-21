
import time 

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.doctor.models import MedicalHistory 
from .data import doctor_personalfamilyhist_post_data, doctor_personalfamilyhist_put_data


def test_post_personalfamily_medical_history(test_client, init_database):
    """
    GIVEN a api end point for medical history assessment
    WHEN the '/doctor/personalfamilyhist/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = doctor_personalfamilyhist_post_data
    
    # send get request for client info on user_id = 1 
    response = test_client.post('/doctor/personalfamilyhist/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 201
    assert response.json[0]['medical_condition_id'] == 1
    assert response.json[0]['myself'] == True
    assert response.json[0]['father'] == True
    assert response.json[0]['mother'] == True
    assert response.json[0]['sister'] == True
    assert response.json[0]['brother'] == True   
    assert response.json[1]['medical_condition_id'] == 2             

def test_put_personalfamily_medical_history(test_client, init_database):
    """
    GIVEN a api end point for personal and family medical history assessment
    WHEN the '/doctor/personalfamilyhist/<user id>/' resource  is requested (PUT)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = doctor_personalfamilyhist_put_data
    
    # send get request for client info on user_id = 1 
    response = test_client.put('/doctor/personalfamilyhist/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201
    assert response.json[0]['medical_condition_id'] == 1
    assert response.json[0]['myself'] == False
    assert response.json[0]['father'] == False
    assert response.json[0]['mother'] == False
    assert response.json[0]['sister'] == False
    assert response.json[0]['brother'] == False 


def test_get_personalfamily_medical_history(test_client, init_database):
    """
    GIVEN a api end point for retrieving personal and family medical history
    WHEN the  '/doctor/personalfamilyhist/<user id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on user_id = 1 
    response = test_client.get('/doctor/personalfamilyhist/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    assert response.json[0]['medical_condition_id'] == 2
    assert response.json[0]['myself'] == False
    assert response.json[0]['father'] == False
    assert response.json[0]['mother'] == False
    assert response.json[0]['sister'] == False
    assert response.json[0]['brother'] == False 
    assert response.json[1]['medical_condition_id'] == 1
    assert response.json[1]['myself'] == False
    assert response.json[1]['father'] == False
    assert response.json[1]['mother'] == False
    assert response.json[1]['sister'] == False
    assert response.json[1]['brother'] == False      