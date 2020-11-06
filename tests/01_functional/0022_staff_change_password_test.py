import datetime
import pathlib
import time

from flask.json import dumps
from requests.auth import _basic_auth_str

from odyssey.models.staff import Staff
from tests.data.staff.staff_data import staff_user_passwords_data
from werkzeug.security import check_password_hash

def test_password_update(test_client, init_database):
    """
    GIVEN a api end point for creating a link for recovering passwords 
    WHEN the '/staff/password/update' PUT resource is requested
    THEN check the response is valid
    """
    # Get staff member to update password
    staff = Staff.query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}
 
    ###
    # Update Password with the correct current password and a 
    # valid new password
    ###
    payload = {"current_password": staff_user_passwords_data["current_password"],
                "new_password": staff_user_passwords_data["new_password"]
    }

    response = test_client.post('/staff/password/update',
                                headers=headers,
                                data=dumps(payload), 
                                content_type='application/json')
    
    # bring up staff member again for updated data
    staff = Staff.query.filter_by(email=staff.email).first()

    assert response.status_code == 200
    assert check_password_hash(staff.password, staff_user_passwords_data['new_password'])    

    ###
    # Update Password with the incorrect current password and a 
    # valid new password
    ###

    response = test_client.post('/staff/password/update',
                                headers=headers,
                                data=dumps(payload), 
                                content_type='application/json')
    
    assert response.status_code == 401
    



