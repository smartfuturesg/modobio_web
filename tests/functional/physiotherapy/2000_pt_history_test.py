
import time 

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.physiotherapy.models import PTHistory 
from .data import pt_history_data


def test_post_pt_history(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for pt history assessment
    WHEN the '/physiotherapy/history/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data

    

    payload = pt_history_data
    
    # For COVERAGE, raise a ContentNotFound error
    # send get request for client info on user_id = 1
    response = test_client.get('/physiotherapy/history/1/',
                                headers=staff_auth_header, 
                                content_type='application/json')
    assert response.status_code == 204

    # For coverage, raise a UserNotFound error
    # send get request for client info on user_id = 1 
    response = test_client.put('/physiotherapy/history/1/',
                                headers=staff_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 404  

    # send get request for client info on user_id = 1 
    response = test_client.post('/physiotherapy/history/1/',
                                headers=staff_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201
    assert response.json['exercise'] == pt_history_data['exercise']
    assert response.json['best_pain'] == pt_history_data['best_pain']    

def test_put_pt_history(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for pt history assessment
    WHEN the '/physiotherapy/history/<user_id>' resource  is requested (PUT)
    THEN check the response is valid
    """
    # get staff authorization to view client data

    

    pt_history_data["exercise"] = "test put"
    payload = pt_history_data
    
    # For COVERAGE, raise an IllegalSettings Error
    # send get request for client info on user_id = 1 
    response = test_client.post('/physiotherapy/history/1/',
                                headers=staff_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 400

    # send get request for client info on user_id = 1 
    response = test_client.put('/physiotherapy/history/1/',
                                headers=staff_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')

    client = PTHistory.query.filter_by(user_id=1).first()

    assert response.status_code == 200
    assert client.exercise == "test put"

def test_get_pt_history(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for retrieving pt history
    WHEN the  '/physiotherapy/history/<user_id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data

    



    # send get request for client info on user_id = 1 
    response = test_client.get('/physiotherapy/history/1/',
                                headers=staff_auth_header, 
                                content_type='application/json')                
    assert response.status_code == 200
    assert response.json['exercise'] == 'test put'
    assert response.json['best_pain'] == 7

