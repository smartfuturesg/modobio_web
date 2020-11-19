
import time 

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.trainer.models import StrengthAssessment 
from tests.data import test_movement_assessment


def test_post_movement_assessment(test_client, init_database):
    """
    GIVEN a api end point for movement assessment
    WHEN the '/trainer/assessment/movement/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = test_movement_assessment
    # send get request for client info on user_id = 1 
    response = test_client.post('/trainer/assessment/movement/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201

def test_get_movement_assessment(test_client, init_database):
    """
    GIVEN a api end point for retrieving all movement assessments
    WHEN the  '/trainer/assessment/movement/<user_id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on user_id = 1 
    response = test_client.get('/trainer/assessment/movement/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200