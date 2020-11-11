
import time 

from flask.json import dumps

from odyssey.models.user import User, UserLogin
from odyssey.models.trainer import HeartAssessment 
from tests.data.trainer.trainer_data import trainer_heart_assessment_data, trainer_medical_physical_data

def test_post_heart_assessment(test_client, init_database):
    """
    GIVEN a api end point for heart assessment
    WHEN the '/trainer/assessment/heart/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    ## the cardio assessment requires the client's vital weight in order to work
    # this is pulled from the medical physical data
    # so we submit a medical physical exam first
    payload = trainer_medical_physical_data
    
    # send get request for client info on user_id = 1 
    response = test_client.post('/doctor/physical/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')


    payload = trainer_heart_assessment_data
    # send get request for client info on clientid = 1 
    response = test_client.post('/trainer/assessment/heart/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201

def test_get_heart_assessment(test_client, init_database):
    """
    GIVEN a api end point for retrieving all heart assessments
    WHEN the  '/trainer/assessment/heart/<user_id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on user_id = 1 
    response = test_client.get('/trainer/assessment/heart/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200