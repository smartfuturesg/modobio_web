import time 

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin

# Test activity tracker look up

def test_get_all_activity_trackers(test_client, init_database, staff_auth_header):
    """
    GIVEN an api end point for looking up all stored activity trackers
    WHEN the  '/wearables/lookupactivitytrackers/all/ resource  is requested (GET)
    THEN check the response is valid
    """

    response = test_client.get('/wearables/lookupactivitytrackers/all/', headers=staff_auth_header)

    assert response.status_code == 200
    assert response.json['total_items'] == 62
    assert len(response.json['items']) == 62

def test_get_apple_activity_trackers(test_client, init_database, staff_auth_header):
    """
    GIVEN an api end point for looking up apple activity trackers
    WHEN the  '/wearables/lookupactivitytrackers/apple/' resource  is requested (GET)
    THEN check the response is valid
    """

    response = test_client.get('/wearables/lookupactivitytrackers/apple/', headers=staff_auth_header)

    assert response.status_code == 200
    assert response.json['total_items'] == 5
    assert len(response.json['items']) == 5   

def test_get_fitbit_activity_trackers(test_client, init_database, staff_auth_header):
    """
    GIVEN an api end point for looking up fitbit activity trackers
    WHEN the  '/wearables/lookupactivitytrackers/fitbit/' resource  is requested (GET)
    THEN check the response is valid
    """

    response = test_client.get('/wearables/lookupactivitytrackers/fitbit/', headers=staff_auth_header)

    assert response.status_code == 200
    assert response.json['total_items'] == 6
    assert len(response.json['items']) == 6        

def test_get_misc_activity_trackers(test_client, init_database, staff_auth_header):
    """
    GIVEN an api end point for looking up misc activity trackers
    WHEN the  '/wearables/lookupactivitytrackers/misc/' resource  is requested (GET)
    THEN check the response is valid
    """

    response = test_client.get('/wearables/lookupactivitytrackers/misc/', headers=staff_auth_header)

    assert response.status_code == 200
    assert response.json['total_items'] == 17
    assert len(response.json['items']) == 17      