
import time 

from flask.json import dumps
from sqlalchemy import select

from odyssey.api.telehealth.models import TelehealthChatRooms

from .data import (
    telehealth_client_staff_bookings_post_1_data,
    telehealth_client_staff_bookings_post_2_data,
    telehealth_client_staff_bookings_post_3_data,
    telehealth_client_staff_bookings_post_4_data,
    telehealth_client_staff_bookings_post_5_data,
    telehealth_client_staff_bookings_post_6_data,
    telehealth_client_staff_bookings_put_1_data
)

# XXX: temporary fix for failing Twilio tests
# import pytest
# pytest.skip('Out of TwiliCoin.', allow_module_level=True)

def test_post_1_client_staff_bookings(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for client staff bookings
    WHEN the '/telehealth/bookings/<int:client_user_id>/<int:staff_user_id>/' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.post('/telehealth/bookings/?client_user_id={}&staff_user_id={}'.format(1,2),
                                headers=staff_auth_header, 
                                data=dumps(telehealth_client_staff_bookings_post_1_data), 
                                content_type='application/json')
                                
    # Bring up conversation to ensure it was created for this booking
    conversation = init_database.session.execute(
        select(TelehealthChatRooms).
        where(TelehealthChatRooms.staff_user_id == 2, TelehealthChatRooms.client_user_id == 1)
    ).one_or_none()[0]

    assert response.status_code == 201
    assert conversation.staff_user_id == 2
    assert conversation.client_user_id == 1
    assert conversation.booking_id == 1

def test_post_2_client_staff_bookings(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for client staff bookings
    WHEN the '/telehealth/bookings/<int:client_user_id>/<int:staff_user_id>/' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.post('/telehealth/bookings/?client_user_id={}&staff_user_id={}'.format(1,2),
                                headers=staff_auth_header, 
                                data=dumps(telehealth_client_staff_bookings_post_2_data), 
                                content_type='application/json')
    assert response.status_code == 201    

def test_post_3_client_staff_bookings(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for client staff bookings
    WHEN the '/telehealth/bookings/<int:client_user_id>/<int:staff_user_id>/' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.post('/telehealth/bookings/?client_user_id={}&staff_user_id={}'.format(1,2),
                                headers=staff_auth_header, 
                                data=dumps(telehealth_client_staff_bookings_post_3_data), 
                                content_type='application/json')
    assert response.status_code == 405   

def test_post_4_client_staff_bookings(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for client staff bookings
    WHEN the '/telehealth/bookings/<int:client_user_id>/<int:staff_user_id>/' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.post('/telehealth/bookings/?client_user_id={}&staff_user_id={}'.format(1,2),
                                headers=staff_auth_header, 
                                data=dumps(telehealth_client_staff_bookings_post_3_data), 
                                content_type='application/json')
    assert response.status_code == 405

def test_post_5_client_staff_bookings(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for client staff bookings
    WHEN the '/telehealth/bookings/<int:client_user_id>/<int:staff_user_id>/' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.post('/telehealth/bookings/?client_user_id={}&staff_user_id={}'.format(1,2),
                                headers=staff_auth_header, 
                                data=dumps(telehealth_client_staff_bookings_post_3_data), 
                                content_type='application/json')
    assert response.status_code == 405        

def test_post_6_client_staff_bookings(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for client staff bookings
    WHEN the '/telehealth/bookings/<int:client_user_id>/<int:staff_user_id>/' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.post('/telehealth/bookings/?client_user_id={}&staff_user_id={}'.format(1,2),
                                headers=staff_auth_header, 
                                data=dumps(telehealth_client_staff_bookings_post_3_data), 
                                content_type='application/json')
    assert response.status_code == 405

def test_get_1_staff_bookings(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for staff bookings
    WHEN the '/telehealth/bookings/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/telehealth/bookings/?staff_user_id={}'.format(2),
                                headers=staff_auth_header, 
                                content_type='application/json')

    assert response.status_code == 200
    
def test_get_2_client_bookings(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for client bookings
    WHEN the '/telehealth/bookings/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/telehealth/bookings/?client_user_id={}'.format(1),
                                headers=client_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200

def test_get_3_staff_client_bookings(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for client bookings
    WHEN the '/telehealth/bookings/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/telehealth/bookings/?client_user_id={}&staff_user_id={}'.format(1,2),
                                headers=staff_auth_header, 
                                content_type='application/json')
    assert response.status_code == 200
    assert response.json['bookings'][0]['status'] == 'Accepted'

def test_put_1_client_staff_bookings(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for client staff bookings
    WHEN the '/telehealth/bookings/<int:client_user_id>/<int:staff_user_id>/' resource  is requested (POST)
    THEN check the response is valid
    """
   
    response = test_client.put('/telehealth/bookings/?booking_id={}'.format(1),
                                headers=staff_auth_header, 
                                data=dumps(telehealth_client_staff_bookings_put_1_data), 
                                content_type='application/json')
    assert response.status_code == 201    

def test_get_4_staff_client_bookings(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for client bookings
    WHEN the '/telehealth/bookings/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/telehealth/bookings/?client_user_id={}&staff_user_id={}'.format(1,2),
                                headers=staff_auth_header, 
                                content_type='application/json')
    assert response.status_code == 200
    assert response.json['bookings'][1]['status'] == 'Completed' 

