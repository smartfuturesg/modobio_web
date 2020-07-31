
import time 

from flask.json import dumps

from odyssey.models.main import Staff
from odyssey.models.pt import PTHistory 
from tests.data import test_pt_history


def test_post_pt_history(test_client, init_database):
    """
    GIVEN a api end point for pt history assessment
    WHEN the '/pt/history/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = test_pt_history
    
    # send get request for client info on clientid = 1 
    response = test_client.post('/api/pt/history/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201


def test_put_pt_history(test_client, init_database):
    """
    GIVEN a api end point for pt history assessment
    WHEN the '/pt/history/<client id>' resource  is requested (PUT)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    test_pt_history["exercise"] = "test put"
    payload = test_pt_history
    
    # send get request for client info on clientid = 1 
    response = test_client.put('/api/pt/history/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')

    client = PTHistory.query.filter_by(clientid=1).first()

    assert response.status_code == 200
    assert client.exercise == "test put"

def test_get_pt_history(test_client, init_database):
    """
    GIVEN a api end point for retrieving pt history
    WHEN the  '/pt/history/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on clientid = 1 
    response = test_client.get('/api/pt/history/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    
