
import time 

from flask.json import dumps

from odyssey.models.staff import Staff
from tests.data import test_client_external_medical_records


def test_post_medical_record_ids(test_client, init_database):
    """
    GIVEN a api end point for posting medical record ids to database
    WHEN the '/doctor/medicalinstitutions/recordid/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = test_client_external_medical_records
    
    # send get request for client info on clientid = 1 
    response = test_client.post('/doctor/medicalinstitutions/recordid/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 201


def test_get_medical_record_ids(test_client, init_database):
    """
    GIVEN a api end point for retrieving medical record ids
    WHEN the  '/doctor/medicalinstitutions/recordid/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on clientid = 1 
    response = test_client.get('/doctor/medicalinstitutions/recordid/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200

def test_get_medical_institutes(test_client, init_database):
    """
    GIVEN a api end point for retrieving all medical institutes
    WHEN the  '/doctor/medicalinstitutions/' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on clientid = 1 
    response = test_client.get('/doctor/medicalinstitutions/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    
