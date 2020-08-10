
import time 

from flask.json import dumps

from odyssey.models.main import Staff
from odyssey.models.doctor import MedicalHistory 
from tests.data import test_medical_history


def test_post_medical_history(test_client, init_database):
    """
    GIVEN a api end point for medical history assessment
    WHEN the '/doctor/medicalhistory/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = test_medical_history
    
    # send get request for client info on clientid = 1 
    response = test_client.post('/doctor/medicalhistory/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 201

def test_put_medical_history(test_client, init_database):
    """
    GIVEN a api end point for medical history assessment
    WHEN the '/doctor/medicalhistory/<client id>/' resource  is requested (PUT)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    test_medical_history["diagnostic_other"] = "testing put"
    payload = test_medical_history
    
    # send get request for client info on clientid = 1 
    response = test_client.put('/doctor/medicalhistory/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')

    client = MedicalHistory.query.filter_by(clientid=1).first()

    assert response.status_code == 200
    assert client.diagnostic_other == "testing put"


def test_get_medical_history(test_client, init_database):
    """
    GIVEN a api end point for retrieving medical history
    WHEN the  '/doctor/medicalhistory/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on clientid = 1 
    response = test_client.get('/doctor/medicalhistory/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    
