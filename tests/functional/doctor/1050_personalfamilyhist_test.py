
import time 

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.doctor.models import MedicalHistory, MedicalFamilyHistory
from .data import doctor_personalfamilyhist_post_data, doctor_personalfamilyhist_put_data


def test_post_personalfamily_medical_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for medical history assessment
    WHEN the '/doctor/familyhistory/<user_id>' resource  is requested (POST)
    By a logged-in CLIENT
    THEN check the response is valid
    """
   

    payload = doctor_personalfamilyhist_post_data
    
    # send post request for client family history on user_id = 1 
    response = test_client.post('/doctor/familyhistory/1/',
                                headers=client_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')
                                
    client_data = MedicalFamilyHistory.query.filter_by(user_id=1).all()

    assert response.status_code == 201
    assert response.json['total_items'] == 2
    assert len(response.json['items']) == 2
    assert len(client_data) == 2           

def test_put_personalfamily_medical_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for personal and family medical history assessment
    WHEN the '/doctor/familyhistory/<user id>/' resource  is requested (PUT)
    THEN check the response is valid
    """
    payload = doctor_personalfamilyhist_put_data
    
    # send put request for client family history on user_id = 1 
    response = test_client.put('/doctor/familyhistory/1/',
                                headers=client_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 201
    assert response.json['total_items'] == 2
    assert len(response.json['items']) == 2


def test_get_personalfamily_medical_history(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for retrieving personal and family medical history
    WHEN the  '/doctor/familyhistory/<user id>' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        # send get request for client family history on user_id = 1 
        response = test_client.get('/doctor/familyhistory/1/',
                                    headers=header, 
                                    content_type='application/json')
                                    
        assert response.status_code == 200
        assert response.json['total_items'] == 3
        assert len(response.json['items']) == 3