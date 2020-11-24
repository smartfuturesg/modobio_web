
import time 

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.doctor.models import MedicalHistory 
from .data import doctor_generalmedicalhist_post_data, doctor_generalmedicalhist_put_data


def test_post_general_medical_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for general medical history assessment
    WHEN the '/doctor/medicalgeneralinfo/<user_id>' resource  is requested (POST)
    By a logged-in CLIENT
    THEN check the response is valid
    """
   
    payload = doctor_generalmedicalhist_post_data
    
    # send post request for client family history on user_id = 1 
    response = test_client.post('/doctor/medicalgeneralinfo/1/',
                                headers=client_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 201 
    assert response.json['genInfo']['primary_doctor_contact_name'] == 'Dr Guy'
    assert response.json['medications'][0]['medication_supplements'] == 'medName1'
    assert len(response.json['medications']) == 2
    assert response.json['allergies'][0]['allergic_to_meds_name'] == 'medName3'
    assert len(response.json['allergies']) == 2

def test_put_general_medical_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for general medical history assessment
    WHEN the '/doctor/medicalgeneralinfo/<user id>/' resource  is requested (PUT)
    THEN check the response is valid
    """
    payload = doctor_generalmedicalhist_put_data
    
    # send put request for client family history on user_id = 1 
    response = test_client.put('/doctor/medicalgeneralinfo/1/',
                                headers=client_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201
    assert response.json['genInfo']['primary_doctor_contact_name'] == 'Dr Guy'
    assert response.json['medications'][0]['medication_supplements'] == 'medName4'
    assert len(response.json['medications']) == 2
    assert response.json['allergies'][0]['allergic_to_meds_name'] == 'medName3'
    assert len(response.json['allergies']) == 2


def test_get_general_medical_history(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for retrieving general medical history
    WHEN the  '/doctor/medicalgeneralinfo/<user id>' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        # send get request for client family history on user_id = 1 
        response = test_client.get('/doctor/medicalgeneralinfo/1/',
                                    headers=header, 
                                    content_type='application/json')
                                    
        assert response.status_code == 200
        assert response.json['genInfo']['primary_doctor_contact_name'] == 'Dr Guy'
        assert response.json['medications'][0]['medication_supplements'] == 'medName1'
        assert len(response.json['medications']) == 3
        assert response.json['allergies'][0]['allergic_to_meds_name'] == 'medName3'
        assert len(response.json['allergies']) == 3        