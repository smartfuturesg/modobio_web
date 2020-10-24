
import time 

from flask.json import dumps

from odyssey.models.user import User, UserLogin
from odyssey.models.doctor import MedicalBloodTests, MedicalBloodTestResults, MedicalBloodTestResultTypes
from tests.data import test_blood_tests


def test_post_medical_blood_test(test_client, init_database):
    """
    GIVEN a api end point for medical blood test
    WHEN the '/doctor/bloodtest/<user_id>/' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = test_blood_tests
    
    client = User.query.filter_by(is_client=True).first()
    # send post request for client info on user_id = client.user_id
    response = test_client.post('/doctor/bloodtest/' + str(client.user_id) + '/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')
    assert response.status_code == 201

def test_get_client_blood_tests(test_client, init_database):
    """
    GIVEN a api end point for retrieving medical blood test instances
    WHEN the  '/doctor/bloodtest/all/<client id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    client = User.query.filter_by(is_client=True).first()
    # send get request for client blood tests on user_id = client.user_id
    response = test_client.get('/doctor/bloodtest/all/'  + str(client.user_id) + '/',
                                headers=headers, 
                                content_type='application/json')
    assert response.status_code == 200
    
def test_get_blood_test_results(test_client, init_database):
    """
    GIVEN a api end point for retrieving medical blood tests results
    WHEN the  '/doctor/bloodtest/results/<test id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    client = User.query.filter_by(is_client=True).first()
    # send get request for client info on user_id = client.user_id
    response = test_client.get('/doctor/bloodtest/results/' + str(client.user_id) + '/',
                                headers=headers, 
                                content_type='application/json')
    response_data = response.get_json()
    assert response.status_code == 200
    assert response_data['items'][0]['results'][0]['evaluation'] == 'optimal'
    assert response_data['items'][0]['results'][1]['evaluation'] == 'normal'

def test_get_blood_test_result_types(test_client, init_database):
    """
    GIVEN a api end point for retrieving medical blood tests result types
    WHEN the  '/bloodtest/result-types/' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on clientid = 1 
    response = test_client.get('doctor/bloodtest/result-types/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200