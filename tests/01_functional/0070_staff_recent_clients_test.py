import base64

from flask.json import dumps
from requests.auth import _basic_auth_str

from odyssey.models.user import User, UserLogin

from tests.data import (
    test_staff_recent_client
)


def test_get_staff_recent_clients(test_client, init_database):
    """
    GIVEN a api end point for getting staff recent clients list
    WHEN the '/staff/recentclients/' resource  is requested
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    response = test_client.get('/staff/recentclients/',
                                headers=headers,  
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 200

def test_create_staff_recent_client(test_client, init_database):
    """
    GIVEN a api end point for registered a staff recent client
    WHEN the '/staff/recentclients/' resource  is requested to be created
    THEN check the response is 401
    """

    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    response = test_client.post('/staff/recentclients/',
                                headers=headers, 
                                data=dumps(test_staff_recent_client), 
                                content_type='application/json')
                                
    # check that the response is valid
    assert response.status_code == 201