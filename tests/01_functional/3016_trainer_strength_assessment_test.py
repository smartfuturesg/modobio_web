
import time 

from flask.json import dumps

from odyssey.models.staff import Staff
from odyssey.models.trainer import StrengthAssessment 
from tests.data.trainer.trainer_data import trainer_strength_assessment_data

def test_post_strength_assessment(test_client, init_database):
    """
    GIVEN a api end point for strength assessment
    WHEN the '/trainer/assessment/strength/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = trainer_strength_assessment_data
    # send get request for client info on clientid = 1 
    response = test_client.post('/trainer/assessment/strength/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201

def test_get_strength_assessment(test_client, init_database):
    """
    GIVEN a api end point for retrieving all strength assessments
    WHEN the  '/trainer/assessment/strength/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on clientid = 1 
    response = test_client.get('/trainer/assessment/strength/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    
