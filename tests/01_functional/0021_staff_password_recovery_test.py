import datetime
import pathlib
import time

from flask.json import dumps
from requests.auth import _basic_auth_str

from odyssey.models.staff import Staff

from tests.data import test_user_passwords



def test_password_recovery_link(test_client, init_database):
    """
    GIVEN a api end point for creating a link for recovering passwords 
    WHEN the '/staff/password/forgot-password/recovery-link' resource  
    is requested to be created
    THEN check the response is valid
    """
    # Get staff member to reset lost password
    staff = Staff.query.first()
 
    payload = {"email": staff.email}

    response = test_client.post('/staff/password/forgot-password/recovery-link',
                                data=dumps(payload), 
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 200
    assert response.get_json()["token"]

def test_full_password_recovery_routine(test_client, init_database):
    """
    GIVEN a api end points for facilitating password recovery
    WHEN the '/staff/password/forgot-password/recovery-link' resource  
    is requested to be created, a token is returned. 
    This token can be used to change the password by sending a PUT
    request to `staff/password/forgot-password/reset`
    THEN check the response is valid
    """
    # Get staff member to reset lost password
    staff = Staff.query.first()
    
    payload_email = {"email": staff.email}

    response = test_client.post('/staff/password/forgot-password/recovery-link',
                                data=dumps(payload_email), 
                                content_type='application/json')
    
    ##
    # Using the password reset token returned from the request above
    # send put request to reset password with new password in payload
    ##
    pswd_rest_token = response.get_json()["token"]

    payload_password_reset = {"password": test_user_passwords["password"]}

    response = test_client.put(f'/staff/password/forgot-password/reset?reset_token={pswd_rest_token}',
                                data=dumps(payload_password_reset), 
                                content_type='application/json')

    # re-query database for staff member
    staff = Staff.query.filter_by(email=staff.email).first()

    assert response.status_code == 200
    assert staff.check_password(password=payload_password_reset['password'])
