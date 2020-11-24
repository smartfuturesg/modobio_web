
import time 

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.trainer.models import HeartAssessment 
from .data import trainer_heart_assessment_data, trainer_medical_physical_data

def test_post_heart_assessment(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for heart assessment
    WHEN the '/trainer/assessment/heart/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    

    payload = trainer_heart_assessment_data
    # send get request for client info on clientid = 1 
    response = test_client.post('/trainer/assessment/heart/1/',
                                headers=staff_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201
    assert response.json['estimated_vo2_max'] == trainer_heart_assessment_data['estimated_vo2_max']

def test_get_heart_assessment(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for retrieving all heart assessments
    WHEN the  '/trainer/assessment/heart/<user_id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    

    # send get request for client info on user_id = 1 
    response = test_client.get('/trainer/assessment/heart/1/',
                                headers=staff_auth_header, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    assert response.json[0]['estimated_vo2_max'] == 84