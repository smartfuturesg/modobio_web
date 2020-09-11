import time 

from flask.json import dumps

from odyssey.models.staff import Staff
from odyssey.models.doctor import MedicalBloodChemistryThyroid
from tests.data import test_blood_chemistry_thyroid


def test_post_blood_chemistry_thyroid(test_client, init_database):
    """
    GIVEN a api end point for blood test - thyroid
    WHEN the '/doctor/bloodchemistry/thyroid/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = test_blood_chemistry_thyroid
    
    # send get request for client info on clientid = 1 
    response = test_client.post('/doctor/bloodchemistry/thyroid/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 201

def test_put_blood_chemistry_thyroid(test_client, init_database):
    """
    GIVEN a api end point for blood test - thyroid
    WHEN the '/doctor/bloodchemistry/thyroid/<client id>/' resource  is requested (PUT)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    test_blood_chemistry_thyroid["idx"] = 1
    test_blood_chemistry_thyroid["t3_serum_free"] = 2.4
    payload = test_blood_chemistry_thyroid
    
    # send get request for client info on clientid = 1 
    response = test_client.put('/doctor/bloodchemistry/thyroid/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')

    client = MedicalBloodChemistryThyroid.query.filter_by(clientid=1).first()

    assert response.status_code == 200
    assert client.t3_serum_free == 2.4


def test_get_blood_chemistry_thyroid(test_client, init_database):
    """
    GIVEN a api end point for blood chemistry - thyroid
    WHEN the  '/doctor/bloodchemistry/thyroid/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on clientid = 1 
    response = test_client.get('/doctor/bloodchemistry/thyroid/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200