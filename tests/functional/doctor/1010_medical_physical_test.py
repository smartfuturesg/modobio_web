
from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from tests.functional.trainer.data import trainer_medical_physical_data


def test_post_medical_physical(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for medical history assessment
    WHEN the '/doctor/physical/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    payload = trainer_medical_physical_data
    
    # send get request for client info on user_id = 1 
    response = test_client.post('/doctor/physical/1/',
                                headers=staff_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')
    assert response.status_code == 201
    assert response.json['vital_weight'] == trainer_medical_physical_data['vital_weight']
    assert response.json['abdominal_hard'] == trainer_medical_physical_data['abdominal_hard']

def test_get_medical_physical(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for retrieving medical history
    WHEN the  '/doctor/physical/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # send get request for client info on user_id = 1 
    response = test_client.get('/doctor/physical/1/',
                                headers=staff_auth_header, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    assert response.json[0]['vital_weight'] == 110.0
    assert response.json[0]['abdominal_hard'] == True
    assert response.json[0]['reporter_lastname'] == 'testerson'