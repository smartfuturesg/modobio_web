import base64

from flask.json import dumps
from requests.auth import _basic_auth_str

from odyssey.api.user.models import User, UserLogin
from odyssey.api.staff.models import StaffProfile, StaffRoles
from odyssey.utils.constants import ACCESS_ROLES
from tests.data.users.users_data import users_staff_new_user_data


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
                                data=dumps(users_staff_new_user_data), 
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 201
    assert response.json['firstname'] == users_staff_new_user_data['userinfo']['firstname']
    assert response.json['is_staff'] == True
    assert response.json['is_client'] == False

    ###
    # Login (get token) for newly created staff member
    ##

    valid_credentials = base64.b64encode(
        f"{users_staff_new_user_data['userinfo']['email']}:{users_staff_new_user_data['userinfo']['password']}".encode(
            "utf-8")).decode("utf-8")
    
    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post('/staff/token/',
                            headers=headers, 
                            content_type='application/json')
    
    roles = response.get_json()['access_roles']
    assert response.status_code == 201
    assert roles.sort() == users_staff_new_user_data['staffinfo']['access_roles'].sort()

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
                                data=dumps(users_staff_new_user_data), 
                                content_type='application/json')
                                
    # 409 should be returned because user email is already in use
    assert response.status_code == 409


def test_add_roles_to_staff(test_client, init_database):
    """
    GIVEN a api end point for creating a new staff 
    WHEN the '/staff/roles/<user_id>/' resource  is requested to be created
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    payload = {'access_roles': ACCESS_ROLES}
    response = test_client.post(f'/staff/roles/{staff.user_id}/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    staff_roles = StaffRoles.query.filter_by(user_id=staff.user_id).all()
    staff_roles = [x.role for x in staff_roles]
    
    # some simple checks for validity
    assert response.status_code == 201
    assert sorted(staff_roles) == sorted(ACCESS_ROLES)
