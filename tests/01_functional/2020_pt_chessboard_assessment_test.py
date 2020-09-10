
import time 

from flask.json import dumps

from odyssey.models.staff import Staff
from odyssey.models.pt import Chessboard 
from tests.data import test_chessboard_assessment


def test_post_chessboard_assessment(test_client, init_database):
    """
    GIVEN a api end point for chessboard assessment
    WHEN the '/pt/chessboard/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    payload = test_chessboard_assessment
    # send get request for client info on clientid = 1 
    response = test_client.post('/pt/chessboard/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 201

def test_get_chessboard_assessment(test_client, init_database):
    """
    GIVEN a api end point for retrieving all chessboard assessments
    WHEN the  'pt/chessboard/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on clientid = 1 
    response = test_client.get('/pt/chessboard/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    
