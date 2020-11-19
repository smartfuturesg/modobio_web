import datetime
import pathlib
import time

from flask.json import dumps
from requests.auth import _basic_auth_str

from odyssey.models.user import User, UserLogin
from tests.data.users.users_data import users_staff_passwords_data

def test_password_update(test_client, init_database):
    """
    GIVEN a api end point for creating a link for recovering passwords 
    WHEN the '/user/password/update' PUT resource is requested
    THEN check the response is valid
    """
    # Get staff member to update password
    user = User.query.filter_by(is_staff=True).first()
    userLogin = UserLogin.query.filter_by(user_id=user.user_id).one_or_none()
    token = userLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}
    ###
    # Update Password with the correct current password and a 
    # valid new password
    ###
    payload = {"current_password": users_staff_passwords_data["password"],
                "new_password": users_staff_passwords_data["new_password"]
    }

    response = test_client.post('/user/password/update/',
                                headers=headers,
                                data=dumps(payload), 
                                content_type='application/json')

    assert response.status_code == 200
    assert userLogin.check_password(password=users_staff_passwords_data['new_password'])

    ###
    # Update Password with the incorrect current password and a 
    # valid new password
    ###

    response = test_client.post('/user/password/update/',
                                headers=headers,
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 401