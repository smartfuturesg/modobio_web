import time 

from flask.json import dumps

from odyssey.models.staff import Staff
from odyssey.models.doctor import MedicalBloodChemistryA1C
from tests.data import test_blood_chemistry_a1c


def test_post_blood_chemistry_a1c(test_client, init_database):
    """
    GIVEN a api end point for blood test - a1c
    WHEN the '/doctor/bloodchemistry/a1c/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = test_blood_chemistry_a1c
    
    # send get request for client info on clientid = 1 
    response = test_client.post('/doctor/bloodchemistry/a1c/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 201

def test_put_blood_chemistry_a1c(test_client, init_database):
    """
    GIVEN a api end point for blood test - a1c
    WHEN the '/doctor/bloodchemistry/a1c/<client id>/' resource  is requested (PUT)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    test_blood_chemistry_a1c["idx"] = 1
    test_blood_chemistry_a1c["a1c"] = 5.0
    payload = test_blood_chemistry_a1c
    
    # send get request for client info on clientid = 1 
    response = test_client.put('/doctor/bloodchemistry/a1c/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')

    client = MedicalBloodChemistryA1C.query.filter_by(clientid=1).first()

    assert response.status_code == 200
    assert client.a1c == 5.0


def test_get_blood_chemistry_a1c(test_client, init_database):
    """
    GIVEN a api end point for blood chemistry - a1c
    WHEN the  '/doctor/bloodchemistry/a1c/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on clientid = 1 
    response = test_client.get('/doctor/bloodchemistry/a1c/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200