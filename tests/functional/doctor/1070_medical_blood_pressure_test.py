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

# Test blood pressure look up

def test_get_blood_pressure_ranges(test_client, init_database, staff_auth_header):
    """
    GIVEN an api end point for looking up stored blood pressure ranges
    WHEN the  '/doctor/lookupbloodpressureranges/' resource  is requested (GET)
    THEN check the response is valid
    """

    response = test_client.get('/doctor/lookupbloodpressureranges/', headers=staff_auth_header)

    assert response.status_code == 200
    assert response.json['total_items'] == 5
    assert len(response.json['items']) == 5