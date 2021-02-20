
import time 

from flask.json import dumps

from .data import (
    telehealth_queue_client_pool_1_post_data,
    telehealth_queue_client_pool_2_post_data,
    telehealth_queue_client_pool_3_post_data,
    telehealth_queue_client_pool_4_post_data,
    telehealth_queue_client_pool_5_post_data,
    telehealth_queue_client_pool_6_post_data,
    telehealth_queue_client_pool_7_post_data
)

def test_post_1_client_appointment(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for client appointment queue
    WHEN the '/telehealth/queue/client-pool/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.post('/telehealth/queue/client-pool/1/',
                                headers=client_auth_header, 
                                data=dumps(telehealth_queue_client_pool_1_post_data), 
                                content_type='application/json')

    assert response.status_code == 200

def test_post_2_client_appointment(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for client appointment queue
    WHEN the '/telehealth/queue/client-pool/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
    
    response = test_client.post('/telehealth/queue/client-pool/1/',
                                headers=client_auth_header, 
                                data=dumps(telehealth_queue_client_pool_2_post_data), 
                                content_type='application/json')

    assert response.status_code == 200

def test_post_3_client_appointment(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for client appointment queue
    WHEN the '/telehealth/queue/client-pool/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
    response = test_client.post('/telehealth/queue/client-pool/1/',
                                headers=client_auth_header, 
                                data=dumps(telehealth_queue_client_pool_3_post_data), 
                                content_type='application/json')

    assert response.status_code == 200

def test_post_4_client_appointment(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for client appointment queue
    WHEN the '/telehealth/queue/client-pool/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
    
    response = test_client.post('/telehealth/queue/client-pool/1/',
                                headers=client_auth_header, 
                                data=dumps(telehealth_queue_client_pool_4_post_data), 
                                content_type='application/json')

    assert response.status_code == 200

def test_post_5_client_appointment(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for client appointment queue
    WHEN the '/telehealth/queue/client-pool/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
    
    response = test_client.post('/telehealth/queue/client-pool/1/',
                                headers=client_auth_header, 
                                data=dumps(telehealth_queue_client_pool_5_post_data), 
                                content_type='application/json')

    assert response.status_code == 200            

def test_get_1_client_appointment_queue(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for client appointment queue
    WHEN the '/telehealth/queue/client-pool/' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        response = test_client.get('/telehealth/queue/client-pool/',
                                    headers=header, 
                                    content_type='application/json')
        
        # queue order should be 4, 1, 3, 2, 5
        assert response.status_code == 200
        assert [response.json['queue'][0]['target_date'],response.json['queue'][0]['priority']] == ['2025-01-02T02:00:00',False]
        assert [response.json['queue'][1]['target_date'],response.json['queue'][1]['priority']] == ['2025-01-05T02:00:00',False]
        assert [response.json['queue'][2]['target_date'],response.json['queue'][2]['priority']] == ['2025-02-05T02:00:00',False]
        assert [response.json['queue'][3]['target_date'],response.json['queue'][3]['priority']] == ['2025-03-05T02:00:00',False]
        assert [response.json['queue'][4]['target_date'],response.json['queue'][4]['priority']] == ['2025-04-05T02:00:00',False]
        assert response.json['total_queue'] == 5

def test_post_6_client_appointment(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for client appointment queue
    WHEN the '/telehealth/queue/client-pool/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """    
    response = test_client.post('/telehealth/queue/client-pool/1/',
                                headers=client_auth_header, 
                                data=dumps(telehealth_queue_client_pool_6_post_data), 
                                content_type='application/json')

    assert response.status_code == 200            

def test_get_2_client_appointment_queue(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for client appointment queue
    WHEN the '/telehealth/queue/client-pool/' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        # send get request for client blood pressure on user_id = 1 
        response = test_client.get('/telehealth/queue/client-pool/',
                                    headers=header, 
                                    content_type='application/json')
        
        # queue order should be 6, 4, 1, 3, 2, 5
        assert response.status_code == 200
        assert [response.json['queue'][0]['target_date'],response.json['queue'][0]['priority']] == ['2025-02-07T02:00:00',True]
        assert [response.json['queue'][1]['target_date'],response.json['queue'][1]['priority']] == ['2025-01-02T02:00:00',False]
        assert [response.json['queue'][2]['target_date'],response.json['queue'][2]['priority']] == ['2025-01-05T02:00:00',False]
        assert [response.json['queue'][3]['target_date'],response.json['queue'][3]['priority']] == ['2025-02-05T02:00:00',False]
        assert [response.json['queue'][4]['target_date'],response.json['queue'][4]['priority']] == ['2025-03-05T02:00:00',False]
        assert [response.json['queue'][5]['target_date'],response.json['queue'][5]['priority']] == ['2025-04-05T02:00:00',False]
        assert response.json['total_queue'] == 6

def test_post_7_client_appointment(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for client appointment queue
    WHEN the '/telehealth/queue/client-pool/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # This Should Fail because the user already has this target_date in the queue
    response = test_client.post('/telehealth/queue/client-pool/1/',
                                headers=client_auth_header, 
                                data=dumps(telehealth_queue_client_pool_5_post_data), 
                                content_type='application/json')

    assert response.status_code == 405          

def test_get_3_client_appointment_queue(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for client appointment queue
    WHEN the '/telehealth/queue/client-pool/' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        response = test_client.get('/telehealth/queue/client-pool/',
                                    headers=header, 
                                    content_type='application/json')
        
        # queue order should be 6, 4, 1, 3, 2, 5
        # This should be the same as test_get_2
        assert response.status_code == 200
        assert [response.json['queue'][0]['target_date'],response.json['queue'][0]['priority']] == ['2025-02-07T02:00:00',True]
        assert [response.json['queue'][1]['target_date'],response.json['queue'][1]['priority']] == ['2025-01-02T02:00:00',False]
        assert [response.json['queue'][2]['target_date'],response.json['queue'][2]['priority']] == ['2025-01-05T02:00:00',False]
        assert [response.json['queue'][3]['target_date'],response.json['queue'][3]['priority']] == ['2025-02-05T02:00:00',False]
        assert [response.json['queue'][4]['target_date'],response.json['queue'][4]['priority']] == ['2025-03-05T02:00:00',False]
        assert [response.json['queue'][5]['target_date'],response.json['queue'][5]['priority']] == ['2025-04-05T02:00:00',False]
        assert response.json['total_queue'] == 6

def test_delete_1_client_appointment_queue(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for client appointment queue
    WHEN the '/telehealth/queue/client-pool/<user_id>' resource  is requested (DELETE)
    THEN check the response is valid
    """

    payload = telehealth_queue_client_pool_3_post_data

    response = test_client.delete("/telehealth/queue/client-pool/1/",
                                data=dumps(payload),
                                headers=client_auth_header, 
                                content_type='application/json')

    assert response.status_code == 200  

def test_post_8_client_appointment(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for client appointment queue
    WHEN the '/telehealth/queue/client-pool/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """    
    response = test_client.post('/telehealth/queue/client-pool/1/',
                                headers=client_auth_header, 
                                data=dumps(telehealth_queue_client_pool_7_post_data), 
                                content_type='application/json')

    assert response.status_code == 200        

def test_get_4_client_appointment_queue(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for client appointment queue
    WHEN the '/telehealth/queue/client-pool/' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        # send get request for client blood pressure on user_id = 1 
        response = test_client.get('/telehealth/queue/client-pool/',
                                    headers=header, 
                                    content_type='application/json')
        
        # queue order should be 3, 6, 4, 1, 2, 5
        # This should be the same as test_get_2
        assert response.status_code == 200
        assert [response.json['queue'][0]['target_date'],response.json['queue'][0]['priority']] == ['2025-02-05T02:00:00',True]
        assert [response.json['queue'][1]['target_date'],response.json['queue'][1]['priority']] == ['2025-02-07T02:00:00',True]
        assert [response.json['queue'][2]['target_date'],response.json['queue'][2]['priority']] == ['2025-01-02T02:00:00',False]
        assert [response.json['queue'][3]['target_date'],response.json['queue'][3]['priority']] == ['2025-01-05T02:00:00',False]
        assert [response.json['queue'][4]['target_date'],response.json['queue'][4]['priority']] == ['2025-03-05T02:00:00',False]
        assert [response.json['queue'][5]['target_date'],response.json['queue'][5]['priority']] == ['2025-04-05T02:00:00',False]
        assert response.json['total_queue'] == 6    

def test_delete_2_client_appointment_queue(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for client appointment queue
    WHEN the '/telehealth/queue/client-pool/<user_id>' resource  is requested (DELETE)
    THEN check the response is valid
    """

    payload = telehealth_queue_client_pool_4_post_data

    response = test_client.delete("/telehealth/queue/client-pool/1/",
                                data=dumps(payload),
                                headers=client_auth_header, 
                                content_type='application/json')

    assert response.status_code == 200  

def test_get_5_client_appointment_queue(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for client appointment queue
    WHEN the '/telehealth/queue/client-pool/' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        response = test_client.get('/telehealth/queue/client-pool/',
                                    headers=header, 
                                    content_type='application/json')
        
        # queue order should be 3, 6, 4, 1, 2, 5
        # This should be the same as test_get_2
        assert response.status_code == 200
        assert [response.json['queue'][0]['target_date'],response.json['queue'][0]['priority']] == ['2025-02-05T02:00:00',True]
        assert [response.json['queue'][1]['target_date'],response.json['queue'][1]['priority']] == ['2025-02-07T02:00:00',True]
        assert [response.json['queue'][2]['target_date'],response.json['queue'][2]['priority']] == ['2025-01-05T02:00:00',False]
        assert [response.json['queue'][3]['target_date'],response.json['queue'][3]['priority']] == ['2025-03-05T02:00:00',False]
        assert [response.json['queue'][4]['target_date'],response.json['queue'][4]['priority']] == ['2025-04-05T02:00:00',False]
        assert response.json['total_queue'] == 5