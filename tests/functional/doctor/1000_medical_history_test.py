
import time 

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.doctor.models import MedicalHistory 
from .data import doctor_medical_history_data


def test_post_medical_history(test_client, init_database):
    """
    GIVEN a api end point for medical history assessment
    WHEN the '/doctor/medicalhistory/<user_id idasdf=>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = doctor_medical_history_data
    
    # send get request for client info on user_id = 1 
    response = test_client.post('/doctor/medicalhistory/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 201
    assert response.json['concerns'] == doctor_medical_history_data['concerns']

def test_put_medical_history(test_client, init_database):
    """
    GIVEN a api end point for medical history assessment
    WHEN the '/doctor/medicalhistory/<client id>/' resource  is requested (PUT)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    doctor_medical_history_data["diagnostic_other"] = "testing put"
    payload = doctor_medical_history_data
    
    # send get request for client info on user_id = 1 
    response = test_client.put('/doctor/medicalhistory/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')

    client = MedicalHistory.query.filter_by(user_id=1).first()

    assert response.status_code == 200
    assert client.diagnostic_other == "testing put"


def test_get_medical_history(test_client, init_database):
    """
    GIVEN a api end point for retrieving medical history
    WHEN the  '/doctor/medicalhistory/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on user_id = 1 
    response = test_client.get('/doctor/medicalhistory/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    assert response.json['concerns'] == doctor_medical_history_data['concerns']
    assert response.json['diagnostic_other'] == 'testing put'