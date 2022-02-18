from flask.json import dumps
from datetime import datetime


def test_read(test_client):
    """
    Send a get request to the server and assert that the response
    has information regarding maintenance blocks from the DB.
    """
    response = test_client.get(
        f'/maintenance/list/',
        headers=test_client.staff_auth_header)
    assert response.status_code == 200

def test_schedule(test_client):
    response = test_client.post(
        f'/maintenance/schedule/',
        headers=test_client.staff_auth_header)
    assert response.status_code == 200

def test_delete(test_client):
    response = test_client.delete(
        f'/maintenance/delete/',
        headers=test_client.staff_auth_header)
    assert response.status_code == 200
