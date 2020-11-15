
import time 

from flask.json import dumps

from odyssey.models.user import User, UserLogin
from odyssey.models.trainer import PowerAssessment 
from tests.data.trainer.trainer_data import trainer_medical_physical_data, trainer_power_assessment_data

def test_post_power_assessment(test_client, init_database):
    """
    GIVEN a api end point for power assessment
    WHEN the '/trainer/assessment/power/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    payload = trainer_power_assessment_data
    # send get request for client info on user_id = 1 
    response = test_client.post('/trainer/assessment/power/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201
    assert response.json['lower_watts_per_kg'] == trainer_power_assessment_data['lower_watts_per_kg']
    assert response.json['leg_press']['bilateral']['attempt_1'] == trainer_power_assessment_data['leg_press']['bilateral']['attempt_1']

def test_get_power_assessment(test_client, init_database):
    """
    GIVEN a api end point for retrieving all power assessments
    WHEN the  '/trainer/assessment/power/<user_id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on user_id = 1 
    response = test_client.get('/trainer/assessment/power/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    assert response.json[0]['lower_watts_per_kg'] == 100
    assert response.json[0]['leg_press']['bilateral']['attempt_1'] == 21