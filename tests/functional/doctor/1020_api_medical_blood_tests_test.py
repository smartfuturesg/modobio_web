
import time 

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.doctor.models import MedicalBloodTests, MedicalBloodTestResults, MedicalBloodTestResultTypes
from .data import doctor_blood_tests_data


def test_post_medical_blood_test(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for medical blood test
    WHEN the '/doctor/bloodtest/<user_id>/' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data

    

    payload = doctor_blood_tests_data
    
    client = User.query.filter_by(is_client=True).first()
    # send post request for client info on user_id = client.user_id
    response = test_client.post('/doctor/bloodtest/' + str(client.user_id) + '/',
                                headers=staff_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')
    assert response.status_code == 201
    assert response.json['panel_type'] == doctor_blood_tests_data['panel_type']

def test_get_client_blood_tests(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for retrieving medical blood test instances
    WHEN the  '/doctor/bloodtest/all/<client id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data

    

    client = User.query.filter_by(is_client=True).first()
    # send get request for client blood tests on user_id = client.user_id
    response = test_client.get('/doctor/bloodtest/all/'  + str(client.user_id) + '/',
                                headers=staff_auth_header, 
                                content_type='application/json')
    assert response.status_code == 200
    assert response.json['items'][0]['notes'] == 'test2'
    
def test_get_blood_test_results_all(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for retrieving medical blood tests results
    WHEN the  '/doctor/bloodtest/results/all/<test id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data

    

    client = User.query.filter_by(is_client=True).first()
    # send get request for client info on user_id = client.user_id
    response = test_client.get('/doctor/bloodtest/results/all/1/',
                                headers=staff_auth_header, 
                                content_type='application/json')
    response_data = response.get_json()
    assert response.status_code == 200
    assert response.json['test_results'] == 2
    assert response.json['items'][0]['panel_type'] == 'Lipids'

def test_get_blood_test_results(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for retrieving medical blood tests results
    WHEN the  '/doctor/bloodtest/results/<test id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data

    

    client = User.query.filter_by(is_client=True).first()
    # send get request for client info on user_id = client.user_id
    response = test_client.get('/doctor/bloodtest/results/1/',
                                headers=staff_auth_header, 
                                content_type='application/json')
    response_data = response.get_json()
    assert response.status_code == 200
    assert response_data['items'][0]['results'][0]['evaluation'] == 'optimal'
    assert response_data['items'][0]['results'][1]['evaluation'] == 'normal'

def test_get_blood_test_result_types(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for retrieving medical blood tests result types
    WHEN the  '/bloodtest/result-types/' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data

    

    # send get request for client info on clientid = 1 
    response = test_client.get('doctor/bloodtest/result-types/',
                                headers=staff_auth_header, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    assert response.json['items'][0]['result_name'] == 'dihydroxyvitaminD'
    assert response.json['items'][0]['normal_max'] == 60