
import time 

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.trainer.models import LungAssessment 
from tests.data import test_lung_assessment, test_medical_physical


def test_post_lung_assessment(test_client, init_database):
    """
    GIVEN a api end point for lung capacity assessment
    WHEN the '/trainer/assessment/lungcapacity/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    ## the lung assessment requires the client's vital weight in order to work
    # this is pulled from the medical physical data
    # so we submit a medical physical exam first
    payload = test_medical_physical
    
    # send get request for client info on user_id = 1 
    response = test_client.post('/doctor/physical/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')

    payload = test_lung_assessment
    # send get request for client info on user_id = 1 
    response = test_client.post('/trainer/assessment/lungcapacity/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201

def test_get_lung_assessment(test_client, init_database):
    """
    GIVEN a api end point for retrieving all lung assessments
    WHEN the  '/trainer/assessment/lungcapacity/<user_id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on user_id = 1 
    response = test_client.get('/trainer/assessment/lungcapacity/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200