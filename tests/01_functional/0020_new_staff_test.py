import base64

from flask.json import dumps
from requests.auth import _basic_auth_str

from odyssey.models.user import User, UserLogin
from odyssey.models.staff import StaffProfile

from tests.data import (
    test_new_user_staff
)


def test_creating_new_staff(test_client, init_database):
    """
    GIVEN a api end point for creating a new staff 
    WHEN the '/staff' resource  is requested to be created
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    response = test_client.post('/user/staff/',
                                headers=headers, 
                                data=dumps(test_new_user_staff), 
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 201

    ###
    # Login (get token) for newly created staff member
    ##

    valid_credentials = base64.b64encode(
        f"{test_new_user_staff['userinfo']['email']}:{test_new_user_staff['userinfo']['password']}".encode(
            "utf-8")).decode("utf-8")
    
    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post('/tokens/staff/',
                            headers=headers, 
                            content_type='application/json')
    
    roles = response.get_json()['access_roles']
    assert response.status_code == 201
    assert roles.sort() == test_new_user_staff['staffinfo']['access_roles'].sort()

def test_creating_new_staff_same_email(test_client, init_database):
    """
    GIVEN a api end point for creating a new staff 
    WHEN the '/staff/' resource  is requested to be created
    THEN check the response is 409 error
    """

    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    response = test_client.post('/user/staff/',
                                headers=headers, 
                                data=dumps(test_new_user_staff), 
                                content_type='application/json')
                                
    # 409 should be returned because user email is already in use
    assert response.status_code == 409