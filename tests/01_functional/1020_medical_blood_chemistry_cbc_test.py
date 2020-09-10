
import time 

from flask.json import dumps

from odyssey.models.staff import Staff
from odyssey.models.doctor import MedicalBloodChemistryCBC 
from tests.data import test_blood_chemistry_cbc


def test_post_medical_blood_chemistry_cbc(test_client, init_database):
    """
    GIVEN a api end point for medical blood chemistry cbc assessment
    WHEN the '/doctor/bloodtest/cbc/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = test_blood_chemistry_cbc
    
    # send get request for client info on clientid = 1 
    response = test_client.post('/doctor/bloodtest/cbc/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 201

def test_put_medical_blood_chemistry_cbc(test_client, init_database):
    """
    GIVEN a api end point for medical blood chemistry cbc assessment
    WHEN the '/doctor/bloodtest/cbc/<client id>/' resource  is requested (PUT)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    test_blood_chemistry_cbc["rbc"] = 30
    payload = test_blood_chemistry_cbc
    
    # send get request for client info on clientid = 1 
    response = test_client.put('/doctor/bloodtest/cbc/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')

    client = MedicalBloodChemistryCBC.query.filter_by(clientid=1).first()

    assert response.status_code == 200
    assert client.rbc == 30


def test_get_medical_blood_chemistry_cbc(test_client, init_database):
    """
    GIVEN a api end point for retrieving blood chemistry cbc history
    WHEN the  '/doctor/bloodtest/cbc/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on clientid = 1 
    response = test_client.get('/doctor/bloodtest/cbc/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    
