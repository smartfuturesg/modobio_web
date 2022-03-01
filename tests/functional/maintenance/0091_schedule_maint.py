from flask import current_app
from flask.json import dumps
import json
from datetime import datetime, timedelta, timezone
import pytz


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
    """
    Schedule a test maintenan=ce block (1 month out)
    """
    zone = pytz.timezone(current_app.config['MAINTENANCE_TIMEZONE'])
    start = (datetime.now(tz=zone) + timedelta(days=30)).isoformat()
    end = (datetime.now(tz=zone) + timedelta(days=30, hours=1)).isoformat()

    response = test_client.post(
        f'/maintenance/schedule/',
        headers=test_client.staff_auth_header,
        data=dumps({"start_time": start, 
                            "end_time": end,
                            "comments": "Test comment"}))
    print(response)
    assert response.status_code == 200

def test_delete(test_client):
    """
    Delete the maintenance block scheduled by the test_schedule function
    """
    get_blocks = test_client.get(
        f'/maintenance/list/',
        headers=test_client.staff_auth_header)

    block_id = json.loads(get_blocks.data)[0]['block_id']
    response = test_client.delete(
        f'/maintenance/delete/',
        headers=test_client.staff_auth_header,
        data=dumps({"block_id": block_id}))
    print(response)
    assert response.status_code == 200
