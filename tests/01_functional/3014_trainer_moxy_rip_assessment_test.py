
import time 

from flask.json import dumps

from odyssey.models.user import User, UserLogin
from odyssey.models.trainer import MoxyRipTest 
from tests.data.trainer.trainer_data import trainer_moxy_rip_data, trainer_medical_physical_data

def test_post_moxy_rip_assessment(test_client, init_database):
    """
    GIVEN a api end point for moxy rip assessment
    WHEN the '/trainer/assessment/moxyrip/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = trainer_moxy_rip_data
    # send get request for client info on clientid = 1 
    response = test_client.post('/trainer/assessment/moxyrip/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201
    assert response.json['vl_side'] == trainer_moxy_rip_data['vl_side']
    assert response.json['performance']['two']['thb'] == trainer_moxy_rip_data['performance']['two']['thb']

def test_get_moxy_rip_assessment(test_client, init_database):
    """
    GIVEN a api end point for retrieving all moxy rip assessments
    WHEN the  '/trainer/assessment/moxyrip/<user_id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on user_id = 1 
    response = test_client.get('/trainer/assessment/moxyrip/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    assert response.json[0]['performance']['two']['thb'] == 10    