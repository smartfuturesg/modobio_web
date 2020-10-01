import datetime
import pathlib
import time

from flask.json import dumps
from requests.auth import _basic_auth_str

from odyssey.models.staff import Staff

def test_get_staff_search(test_client, init_database):
    """
    GIVEN a api end point for retrieving client info
    WHEN the '/client/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    # Order of test search:
    # send staffid
    # firstname
    # lastname
    # email
    # firstname and email
    # FORCE 404 staffid = 2 

    # send get request for staff staffid = 1
    response = test_client.get('/staff/?staffid=1', headers=headers)
    assert response.status_code == 200

    # send get request for first name (note, the actual first name is testY)
    response = test_client.get('/staff/?firstname=test', headers=headers)
    assert response.status_code == 200
    assert response.json[0]['firstname'] == 'testy'
    assert response.json[0]['lastname'] == 'testerson'
    assert response.json[0]['email'] == 'staff_member@modobio.com'
    assert response.json[0]['staffid'] == 1

    # send get request for last name
    response = test_client.get('/staff/?lastname=test', headers=headers)
    assert response.json[0]['firstname'] == 'testy'
    assert response.json[0]['lastname'] == 'testerson'
    assert response.json[0]['email'] == 'staff_member@modobio.com'
    assert response.json[0]['staffid'] == 1
    
    # send get request for email
    response = test_client.get('/staff/?email=staff_member@modobio.com', headers=headers)
    assert response.json[0]['firstname'] == 'testy'
    assert response.json[0]['lastname'] == 'testerson'
    assert response.json[0]['email'] == 'staff_member@modobio.com'
    assert response.json[0]['staffid'] == 1

    # send get request for first name (note, the actual first name is testY)
    response = test_client.get('/staff/?firstname=test&email=staff_member@modobio.com', headers=headers)
    assert response.json[0]['firstname'] == 'testy'
    assert response.json[0]['lastname'] == 'testerson'
    assert response.json[0]['email'] == 'staff_member@modobio.com'
    assert response.json[0]['staffid'] == 1

    # Expect response to fail because there is only one staff
    response = test_client.get('/staff/?staffid=2', headers=headers)
    assert response.status_code == 404
