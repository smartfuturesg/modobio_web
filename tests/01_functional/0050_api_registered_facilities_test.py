from flask.json import dumps

from odyssey.models.staff import Staff
from odyssey.models.client import ClientFacilities
from odyssey.models.misc import RegisteredFacilities
from tests.data.registeredfacilities.registeredfacilities_data import (
    registeredfacilities_registered_facilities_data, 
    registeredfacilities_client_facilities_data
)

def test_post_registered_facilities(test_client, init_database):
    """
    GIVEN a api end point for blood test - a1c
    WHEN the '/doctor/bloodchemistry/a1c/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = registeredfacilities_registered_facilities_data
    
    # send psot request for a new facility 
    response = test_client.post('/registeredfacility/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 201

def test_put_registered_facility(test_client, init_database):
    """
    GIVEN a api end point for registered facility
    WHEN the '/registeredfacility/<facility id>/' resource  is requested (PUT)
    THEN check the response is valid
    """
    # get staff authorization to view facility data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    registerfacilities_registered_facilities_data["facility_address"] = "123 Test Address"
    payload = registerfacilities_registered_facilities_data
    
    # send get request for facility info on facility_id = 1
    response = test_client.put('/registeredfacility/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')

    facility = RegisteredFacilities.query.filter_by(facility_id=1).first()

    assert response.status_code == 200
    assert facility.facility_address == "123 Test Address"

def test_get_registered_facility(test_client, init_database):
    """
    GIVEN a api end point for registered facility
    WHEN the  '/registeredfacility/<facility id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view facility data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for facility info on facility_id = 1 
    response = test_client.get('/registeredfacility/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200

def test_post_client_facility(test_client, init_database):
    """
    GIVEN a api end point for client facility
    WHEN the '/registeredfacility/client/<client id>' resource is requested (POST)
    THEN check the response is valid
    """
    #get staff authorization to view facility data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = registeredfacilities_client_facilities_data

    #send post request for a client-facility relation with facility_id = 1 and client_id = 1
    response = test_client.post('/registeredfacility/client/1/',
                                 headers=headers,
                                 data=dumps(payload),
                                 content_type='application/json')

    assert response.status_code == 201

def test_get_client_facility(test_client, init_database):
    """
    GIVEN a api end point for client facility
    WHEN the '/registeredfacility/client/<client id>' resource is requested (GET)
    THEN check the response is valid
    """
    #get staff authorization to view facility data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    #send post request for a client-facility relation with facility_id = 1 and client_id = 1
    response = test_client.get('/registeredfacility/client/1/',
                                 headers=headers,
                                 content_type='application/json')

    assert response.status_code == 200

def test_get_client_summary(test_client, init_database):
    """
    GIVEN a api end point for cient sidebar
    WHEN the '/client/sidebar/<client id>' resource is requested (GET)
    THEN check the response is valid
    """
    #get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    #send get request for a client with client id = 1
    response = test_client.get('/client/summary/1/',
                                headers=headers,
                                content_type='application/json')

    assert response.status_code == 200