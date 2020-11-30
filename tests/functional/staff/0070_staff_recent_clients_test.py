import base64

from flask.json import dumps
from requests.auth import _basic_auth_str

from odyssey.api.user.models import User, UserLogin

def test_get_staff_recent_clients(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for getting staff recent clients list
    WHEN the '/staff/recentclients/' resource  is requested
    THEN check the response is valid
    """
    # get staff authorization to view client data

    

    response = test_client.get('/staff/recentclients/',
                                headers=staff_auth_header,  
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 200