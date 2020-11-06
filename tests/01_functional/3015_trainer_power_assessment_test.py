
import time 

from flask.json import dumps

from odyssey.models.staff import Staff
from odyssey.models.trainer import PowerAssessment 
from tests.data.trainer.trainer_data import trainer_medical_physical_data, trainer_power_assessment_data

def test_post_power_assessment(test_client, init_database):
    """
    GIVEN a api end point for power assessment
    WHEN the '/trainer/assessment/power/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    ## the power assessment requires the client's vital weight in order to work
    # this is pulled from the medical physical data
    # so we submit a medical physical exam first
    payload = trainer_medical_physical_data
    
    # send get request for client info on clientid = 1 
    response = test_client.post('/doctor/physical/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')

    payload = trainer_power_assessment_data
    # send get request for client info on clientid = 1 
    response = test_client.post('/trainer/assessment/power/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201

def test_get_power_assessment(test_client, init_database):
    """
    GIVEN a api end point for retrieving all power assessments
    WHEN the  '/trainer/assessment/power/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on clientid = 1 
    response = test_client.get('/trainer/assessment/power/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    
