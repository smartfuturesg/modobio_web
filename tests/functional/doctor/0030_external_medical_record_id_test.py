
import time 

from flask.json import dumps
from odyssey.api.user.models import User, UserLogin
from .data import doctor_clients_external_medical_records_data

def test_post_medical_record_ids(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for posting medical record ids to database
    WHEN the '/doctor/medicalinstitutions/recordid/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    

    payload = doctor_clients_external_medical_records_data
    
    # send get request for client info on user_id = 1 
    response = test_client.post('/doctor/medicalinstitutions/recordid/1/',
                                headers=staff_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 201
    assert response.json['record_locators'][0]['med_record_id'] == doctor_clients_external_medical_records_data['record_locators'][0]['med_record_id']


def test_get_medical_record_ids(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for retrieving medical record ids
    WHEN the  '/doctor/medicalinstitutions/recordid/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    

    # send get request for client info on user_id = 1 
    response = test_client.get('/doctor/medicalinstitutions/recordid/1/',
                                headers=staff_auth_header, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    assert response.json['record_locators'][0]['med_record_id'] == doctor_clients_external_medical_records_data['record_locators'][0]['med_record_id']

def test_get_medical_institutes(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for retrieving all medical institutes
    WHEN the  '/doctor/medicalinstitutions/' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    

    # send get request for client info on user_id = 1 
    response = test_client.get('/doctor/medicalinstitutions/',
                                headers=staff_auth_header, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    assert response.json[0]['institute_name'] == 'Mercy Gilbert Medical Center'
    
