
import time 

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from .data import (
    users_queue_client_pool_1_data,
    users_queue_client_pool_2_data,
    users_queue_client_pool_3_data,
    users_queue_client_pool_4_data,
    users_queue_client_pool_5_data,
    users_queue_client_pool_6_data
)

def test_post_1_client_appointment(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for blood pressure assessment
    WHEN the '/doctor/bloodpressure/<user_id>' resource  is requested (POST)
    By a logged-in CLIENT
    THEN check the response is valid
    """
   
    
    # send post request for client blood pressure on user_id = 1 
    response = test_client.post('/user/queue/client-pool/1/',
                                headers=client_auth_header, 
                                data=dumps(users_queue_client_pool_1_data), 
                                content_type='application/json')

    assert response.status_code == 200

def test_post_2_client_appointment(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for blood pressure assessment
    WHEN the '/doctor/bloodpressure/<user_id>' resource  is requested (POST)
    By a logged-in CLIENT
    THEN check the response is valid
    """
   
    
    # send post request for client blood pressure on user_id = 1 
    response = test_client.post('/user/queue/client-pool/1/',
                                headers=client_auth_header, 
                                data=dumps(users_queue_client_pool_2_data), 
                                content_type='application/json')

    assert response.status_code == 200

def test_post_3_client_appointment(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for blood pressure assessment
    WHEN the '/doctor/bloodpressure/<user_id>' resource  is requested (POST)
    By a logged-in CLIENT
    THEN check the response is valid
    """
    # send post request for client blood pressure on user_id = 1 
    response = test_client.post('/user/queue/client-pool/1/',
                                headers=client_auth_header, 
                                data=dumps(users_queue_client_pool_3_data), 
                                content_type='application/json')

    assert response.status_code == 200

def test_post_4_client_appointment(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for blood pressure assessment
    WHEN the '/doctor/bloodpressure/<user_id>' resource  is requested (POST)
    By a logged-in CLIENT
    THEN check the response is valid
    """
   
    
    # send post request for client blood pressure on user_id = 1 
    response = test_client.post('/user/queue/client-pool/1/',
                                headers=client_auth_header, 
                                data=dumps(users_queue_client_pool_4_data), 
                                content_type='application/json')

    assert response.status_code == 200

def test_post_5_client_appointment(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for blood pressure assessment
    WHEN the '/doctor/bloodpressure/<user_id>' resource  is requested (POST)
    By a logged-in CLIENT
    THEN check the response is valid
    """
   
    
    # send post request for client blood pressure on user_id = 1 
    response = test_client.post('/user/queue/client-pool/1/',
                                headers=client_auth_header, 
                                data=dumps(users_queue_client_pool_5_data), 
                                content_type='application/json')

    assert response.status_code == 200            

def test_get_1_client_appointment_queue(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for retrieving user's blood pressure
    WHEN the  '/doctor/bloodpressure/<user id>' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        # send get request for client blood pressure on user_id = 1 
        response = test_client.get('/user/queue/client-pool/',
                                    headers=header, 
                                    content_type='application/json')
        
        # queue order should be 4, 1, 3, 2, 5
        assert response.status_code == 200
        assert len(response.json['queue']) == 5
        assert response.json['total_queue'] == 5

def test_post_6_client_appointment(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for blood pressure assessment
    WHEN the '/doctor/bloodpressure/<user_id>' resource  is requested (POST)
    By a logged-in CLIENT
    THEN check the response is valid
    """
   
    
    # send post request for client blood pressure on user_id = 1 
    response = test_client.post('/user/queue/client-pool/1/',
                                headers=client_auth_header, 
                                data=dumps(users_queue_client_pool_6_data), 
                                content_type='application/json')

    assert response.status_code == 200            

def test_get_2_client_appointment_queue(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for retrieving user's blood pressure
    WHEN the  '/doctor/bloodpressure/<user id>' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        # send get request for client blood pressure on user_id = 1 
        response = test_client.get('/user/queue/client-pool/',
                                    headers=header, 
                                    content_type='application/json')
        
        # queue order should be 6, 4, 1, 3, 2, 5
        assert response.status_code == 200
        assert len(response.json['queue']) == 6
        assert response.json['total_queue'] == 6

def test_post_7_client_appointment(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for blood pressure assessment
    WHEN the '/doctor/bloodpressure/<user_id>' resource  is requested (POST)
    By a logged-in CLIENT
    THEN check the response is valid
    """
   
    # This Should Fail because the user already has this target_date in the queue
    response = test_client.post('/user/queue/client-pool/1/',
                                headers=client_auth_header, 
                                data=dumps(users_queue_client_pool_5_data), 
                                content_type='application/json')

    assert response.status_code == 405          

def test_get_3_client_appointment_queue(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for retrieving user's blood pressure
    WHEN the  '/doctor/bloodpressure/<user id>' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        # send get request for client blood pressure on user_id = 1 
        response = test_client.get('/user/queue/client-pool/',
                                    headers=header, 
                                    content_type='application/json')
        
        # queue order should be 6, 4, 1, 3, 2, 5
        # This should be the same as test_get_2
        assert response.status_code == 200
        assert len(response.json['queue']) == 6
        assert response.json['total_queue'] == 6