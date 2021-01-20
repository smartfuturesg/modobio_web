import base64

from flask.json import dumps
from requests.auth import _basic_auth_str

from odyssey.api.user.models import User, UserLogin
from odyssey.api.staff.models import StaffProfile, StaffRoles
from odyssey.utils.constants import ACCESS_ROLES
from .data import users_staff_new_user_data


def test_creating_new_staff(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for creating a new staff 
    WHEN the '/staff' resource  is requested to be created
    THEN check the response is valid
    """
    # get staff authorization to view client data
    global new_staff_uid
    
    
    response = test_client.post('/user/staff/',
                                headers=staff_auth_header, 
                                data=dumps(users_staff_new_user_data), 
                                content_type='application/json')
    
    new_staff_uid = response.json['user_info']['user_id']
    # some simple checks for validity
    assert response.status_code == 201
    assert response.json['firstname'] == users_staff_new_user_data['user_info']['firstname']
    assert response.json['is_staff'] == True
    assert response.json['is_client'] == False

def test_get_staff_user_info(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for retrieving staff and user info
    WHEN the '/staff/user_id' resource  is requested
    THEN check the response is valid
    """
    response = test_client.get(f'/user/staff/{new_staff_uid}/',
                                headers=staff_auth_header, 
                                content_type='application/json')

    assert response.status_code == 200
    assert response.json['staff_info']
    assert response.json['user_info']

                

def test_staff_login(test_client, init_database, staff_auth_header):
    """
    GIVEN a api fr requesting an API access token
    WHEN the 'tokens/staff/' resource  is requested to be created
    THEN check the response is valid
    """
    
    ###
    # Login (get token) for newly created staff member
    ##
    valid_credentials = base64.b64encode(
        f"{users_staff_new_user_data['user_info']['email']}:{users_staff_new_user_data['user_info']['password']}".encode(
            "utf-8")).decode("utf-8")
    
    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post('/staff/token/',
                            headers=headers, 
                            content_type='application/json')
    
    # ensure access roles are correctly returned
    roles = response.get_json()['access_roles']

    assert response.status_code == 201
    assert roles.sort() == users_staff_new_user_data['staff_info']['access_roles'].sort()


def test_creating_new_staff_same_email(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for creating a new staff 
    WHEN the '/staff/' resource  is requested to be created
    THEN check the response is 409 error
    """   
    response = test_client.post('/user/staff/',
                                headers=staff_auth_header, 
                                data=dumps(users_staff_new_user_data), 
                                content_type='application/json')
                                
    # 409 should be returned because user email is already in use
    assert response.status_code == 409


def test_add_roles_to_staff(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for updating a staff member's roles 
    WHEN the '/staff/roles/<user_id>/' resource  is requested to be created
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    payload = {'access_roles': ACCESS_ROLES}
    response = test_client.post(f'/staff/roles/{staff.user_id}/',
                                headers=staff_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    staff_roles = StaffRoles.query.filter_by(user_id=staff.user_id).all()
    staff_roles = [x.role for x in staff_roles]
    
    # some simple checks for validity
    assert response.status_code == 201
    assert sorted(staff_roles) == sorted(ACCESS_ROLES)

def test_check_staff_roles(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for checking a staff member's roles 
    WHEN the '/staff/roles/<user_id>/' resource  is requested GET
    THEN check the response is valid
    """

    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    response = test_client.get(f'/staff/roles/{staff.user_id}/',
                                headers=staff_auth_header, 
                                content_type='application/json')
    
    staff_roles = StaffRoles.query.filter_by(user_id=staff.user_id).all()
    staff_roles = [x.role for x in staff_roles]
    
    # some simple checks for validity
    assert response.status_code == 200
    assert sorted(staff_roles) == sorted(ACCESS_ROLES)

