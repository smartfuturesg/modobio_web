
import time 

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.doctor.models import MedicalHistory 
from .data import (
    doctor_blood_pressures_data
)

def test_post_1_blood_pressure_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for blood pressure assessment
    WHEN the '/doctor/bloodpressure/<user_id>' resource  is requested (POST)
    By a logged-in CLIENT
    THEN check the response is valid
    """
   
    
    # send post request for client blood pressure on user_id = 1 
    response = test_client.post('/doctor/bloodpressure/1/',
                                headers=client_auth_header, 
                                data=dumps(doctor_blood_pressures_data), 
                                content_type='application/json')

    assert response.status_code == 201 

def test_get_1_blood_pressure_history(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for retrieving user's blood pressure
    WHEN the  '/doctor/bloodpressure/<user id>' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        # send get request for client blood pressure on user_id = 1 
        response = test_client.get('/doctor/bloodpressure/1/',
                                    headers=header, 
                                    content_type='application/json')
        
        assert response.status_code == 200
        assert len(response.json['items']) == 1
        assert response.json['total_items'] == 1
