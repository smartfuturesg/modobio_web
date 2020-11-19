
import time 

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.physiotherapy.models import Chessboard 
from tests.data.trainer.trainer_data import trainer_chessboard_assessment_data

def test_post_chessboard_assessment(test_client, init_database):
    """
    GIVEN a api end point for chessboard assessment
    WHEN the '/physiotherapy/chessboard/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    # For COVERAGE, raise ContentNotFound error
    response = test_client.get('/physiotherapy/chessboard/1/',
                                headers=headers, 
                                content_type='application/json')  

    assert response.status_code == 204

    payload = trainer_chessboard_assessment_data
    # send get request for client info on user_id = 1 
    response = test_client.post('/physiotherapy/chessboard/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 201
    assert response.json['isa_structure'] == trainer_chessboard_assessment_data['isa_structure']
    assert response.json['hip']['left']['flexion'] == trainer_chessboard_assessment_data['hip']['left']['flexion']

def test_get_chessboard_assessment(test_client, init_database):
    """
    GIVEN a api end point for retrieving all chessboard assessments
    WHEN the  'physiotherapy/chessboard/<user_id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on user_id = 1 
    response = test_client.get('/physiotherapy/chessboard/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    assert response.json[0]['isa_structure'] == 'Asymmetrical Atypical'
    assert response.json[0]['hip']['left']['flexion'] == 70
