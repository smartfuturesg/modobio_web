import datetime
import pathlib
import time

from flask.json import dumps
from requests.auth import _basic_auth_str

from odyssey.models.staff import Staff

from tests.data import (
    test_new_staff_member,
)


def test_creating_new_staff(test_client, init_database):
    """
    GIVEN a api end point for creating a new staff 
    WHEN the '/staff' resource  is requested to be created
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff.query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}
    # breakpoint()
    response = test_client.post('/staff/',
                                headers=headers, 
                                data=dumps(test_new_staff_member), 
                                content_type='application/json')
    
    #the new client should be in the ClientInfo database 
    staff = Staff.query.filter_by(email=test_new_staff_member['email']).first()
    
    # some simple checks for validity
    assert response.status_code == 201
    assert staff.email == test_new_staff_member['email']
    

def test_creating_new_staff_same_email(test_client, init_database):
    """
    GIVEN a api end point for creating a new staff 
    WHEN the '/staff/' resource  is requested to be created
    THEN check the response is 409 error
    """

    # get staff authorization to view client data
    staff = Staff.query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    response = test_client.post('/staff/',
                                headers=headers, 
                                data=dumps(test_new_staff_member), 
                                content_type='application/json')
    
    #the new client should be in the ClientInfo database 
    
    
    # some simple checks for validity
    assert response.status_code == 409
    


