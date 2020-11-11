from flask.json import dumps
from requests.auth import _basic_auth_str

from odyssey.models.user import User, UserLogin
from odyssey.models.staff import StaffProfile

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
    
    response = test_client.post('/user/',
                                headers=headers, 
                                data=dumps(users_staff_new_user_data['userinfo']), 
                                content_type='application/json')
    
    #the new staff member should be in the StaffProfile database 
    staff = StaffProfile.query.filter_by(user_id=1).one_or_none()
    
    # some simple checks for validity
    assert response.status_code == 201
    
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
    
    response = test_client.post('/user/',
                                headers=headers, 
                                data=dumps(users_staff_new_user_data['userinfo']), 
                                content_type='application/json')
    
    # 409 should be returned because user email is already in use
    assert response.status_code == 409