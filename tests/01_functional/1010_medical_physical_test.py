
from flask.json import dumps

from odyssey.models.staff import Staff
from tests.data.trainer.trainer_data import trainer_medical_physical_data


def test_post_medical_physical(test_client, init_database):
    """
    GIVEN a api end point for medical history assessment
    WHEN the '/doctor/physical/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = trainer_medical_physical_data
    
    # send get request for client info on clientid = 1 
    response = test_client.post('/doctor/physical/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')
    assert response.status_code == 201

def test_get_medical_physical(test_client, init_database):
    """
    GIVEN a api end point for retrieving medical history
    WHEN the  '/doctor/physical/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on clientid = 1 
    response = test_client.get('/doctor/physical/1/',
                                headers=headers, 
                                content_type='application/json')
    assert response.status_code == 200
    
