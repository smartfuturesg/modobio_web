
import time 

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.trainer.models import StrengthAssessment 
from .data import trainer_movement_assessment_data

def test_post_movement_assessment(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for movement assessment
    WHEN the '/trainer/assessment/movement/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data

    

    payload = trainer_movement_assessment_data
    # send get request for client info on clientid = 1 
    response = test_client.post('/trainer/assessment/movement/1/',
                                headers=staff_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201
    assert response.json['toe_touch']['ribcage_movement'][0] == trainer_movement_assessment_data['toe_touch']['ribcage_movement'][0]

def test_get_movement_assessment(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for retrieving all movement assessments
    WHEN the  '/trainer/assessment/movement/<user_id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data

    

    # send get request for client info on user_id = 1 
    response = test_client.get('/trainer/assessment/movement/1/',
                                headers=staff_auth_header, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    assert response.json[0]['toe_touch']['ribcage_movement'][0] == 'Even Bilaterally'
