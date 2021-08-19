import base64

from flask.json import dumps
from requests.auth import _basic_auth_str

from odyssey.api.user.models import User, UserLogin

def test_get_staff_recent_clients(test_client):
    response = test_client.get(
        '/staff/recentclients/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    # some simple checks for validity
    assert response.status_code == 200
