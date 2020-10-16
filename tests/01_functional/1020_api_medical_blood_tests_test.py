
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
    
    # send post request for client info on user_id = 1 
    response = test_client.post('/doctor/bloodtest/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')
    assert response.status_code == 201

def test_get_client_blood_tests(test_client, init_database):
    """
    GIVEN a api end point for retrieving medical blood tests
    WHEN the  '/doctor/bloodtest/<client id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client blood tests on user_id = 1 
    response = test_client.get('/doctor/bloodtest/1/',
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

    # send get request for client info on user_id = 1 
    response = test_client.get('/doctor/bloodtest/results/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200