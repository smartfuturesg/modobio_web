import time 

from flask.json import dumps

from odyssey.models.staff import Staff
from odyssey.models.doctor import MedicalBloodChemistryLipids
from tests.data import test_get_blood_chemistry_lipids


def test_post_blood_chemistry_lipids(test_client, init_database):
    """
    GIVEN a api end point for blood test - lipids
    WHEN the '/doctor/bloodchemistry/lipids/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = test_get_blood_chemistry_lipids
    
    # send get request for client info on clientid = 1 
    response = test_client.post('/doctor/bloodchemistry/lipids/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 201

def test_put_blood_chemistry_lipids(test_client, init_database):
    """
    GIVEN a api end point for blood test - lipids
    WHEN the '/doctor/bloodchemistry/lipids/<client id>/' resource  is requested (PUT)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    test_medical_history["exam_date"] = "1900-01-01"
    payload = test_get_blood_chemistry_lipids
    
    # send get request for client info on clientid = 1 
    response = test_client.put('/doctor/bloodchemistry/lipids/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')

    client = MedicalHistory.query.filter_by(clientid=1).first()

    assert response.status_code == 200
    assert client.exam_date == "1900-01-01"


def test_get_blood_chemistry_lipids(test_client, init_database):
    """
    GIVEN a api end point for blood chemistry - lipids
    WHEN the  '/doctor/bloodchemistry/lipids/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on clientid = 1 
    response = test_client.get('/doctor/bloodchemistry/lipids/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200