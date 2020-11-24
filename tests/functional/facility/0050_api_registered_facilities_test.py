from flask.json import dumps
 
from odyssey.api.user.models import User, UserLogin
from odyssey.api.client.models import ClientFacilities
from odyssey.api.facility.models import RegisteredFacilities
from .data import (
    registeredfacilities_registered_facilities_data, 
    registeredfacilities_client_facilities_data
)

def test_post_registered_facilities(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for blood test - a1c
    WHEN the '/doctor/bloodchemistry/a1c/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data

    

    payload = registeredfacilities_registered_facilities_data

    # send post request for a new facility 
    response = test_client.post('/facility/',
                                headers=staff_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 201



def test_put_registered_facility(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for registered facility
    WHEN the '/facility/<facility id>/' resource  is requested (PUT)
    THEN check the response is valid
    """
    # get staff authorization to view facility data

    

    registeredfacilities_registered_facilities_data["facility_address"] = "123 Test Address"
    payload = registeredfacilities_registered_facilities_data
    
    # send get request for facility info on facility_id = 1
    response = test_client.put('/facility/1/',
                                headers=staff_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')

    facility = RegisteredFacilities.query.filter_by(facility_id=1).first()

    assert response.status_code == 200
    assert facility.facility_address == "123 Test Address"

def test_get_registered_facility(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for registered facility
    WHEN the  '/facility/<facility id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view facility data

    

    # send get request for facility info on facility_id = 1 
    response = test_client.get('/facility/1/',
                                headers=staff_auth_header, 
                                content_type='application/json')
                                
    assert response.status_code == 200

    # send get request for facility info on facility_id = 1 
    response = test_client.get('/facility/all/',
                                headers=staff_auth_header, 
                                content_type='application/json')
                                
    assert response.status_code == 200    

def test_post_client_facility(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for client facility
    WHEN the '/facility/client/<user_id>' resource is requested (POST)
    THEN check the response is valid
    """
    #get staff authorization to view facility data

    

    payload = registeredfacilities_client_facilities_data

    client = User.query.filter_by(is_client=True).first()
    #send post request for a client-facility relation with facility_id = 1 and user_id = client.user_id
    response = test_client.post('/facility/client/' + str(client.user_id) + '/',
                                 headers=staff_auth_header,
                                 data=dumps(payload),
                                 content_type='application/json')

    assert response.status_code == 201

def test_get_client_facility(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for client facility
    WHEN the '/facility/client/<user_id>' resource is requested (GET)
    THEN check the response is valid
    """
    #get staff authorization to view facility data

    

    client = User.query.filter_by(is_client=True).first()
    #send get request for a client with user_id = client.user_id
    response = test_client.get('/facility/client/' + str(client.user_id) + '/',
                                headers=staff_auth_header,
                                content_type='application/json')

    assert response.status_code == 200

def test_get_client_summary(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for cient sidebar
    WHEN the '/client/sidebar/<user_id>' resource is requested (GET)
    THEN check the response is valid
    """
    #get staff authorization to view client data

    

    client = User.query.filter_by(is_client=True).first()
    #send get request for a client with user_id = client.user_id
    response = test_client.get('/client/summary/' + str(client.user_id) + '/',
                                headers=staff_auth_header,
                                content_type='application/json')

    assert response.status_code == 200