
import time 

from flask.json import dumps

from odyssey.models.staff import Staff
from odyssey.models.trainer import MoxyAssessment 
from tests.data.trainer.trainer_data import trainer_moxy_assessment_data

def test_post_moxy_assessment(test_client, init_database):
    """
    GIVEN a api end point for moxy assessment
    WHEN the '/trainer/assessment/moxy/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = trainer_moxy_assessment_data
    # send get request for client info on clientid = 1 
    response = test_client.post('/trainer/assessment/moxy/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201

def test_get_moxy_assessment(test_client, init_database):
    """
    GIVEN a api end point for retrieving all moxy assessments
    WHEN the  '/trainer/assessment/moxy/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on clientid = 1 
    response = test_client.get('/trainer/assessment/moxy/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    
