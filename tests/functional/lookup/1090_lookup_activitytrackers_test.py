import time

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin

# Test activity tracker look up

def test_get_all_activity_trackers(test_client):
    response = test_client.get(
        '/lookup/activity-trackers/all/', headers=test_client.staff_auth_header)

    assert response.status_code == 200
    assert response.json['total_items'] == 62
    assert len(response.json['items']) == 62

def test_get_apple_activity_trackers(test_client):
    response = test_client.get(
        '/lookup/activity-trackers/apple/', headers=test_client.staff_auth_header)

    assert response.status_code == 200
    assert response.json['total_items'] == 5
    assert len(response.json['items']) == 5

def test_get_fitbit_activity_trackers(test_client):
    response = test_client.get(
        '/lookup/activity-trackers/fitbit/', headers=test_client.staff_auth_header)

    assert response.status_code == 200
    assert response.json['total_items'] == 6
    assert len(response.json['items']) == 6

def test_get_misc_activity_trackers(test_client):
    response = test_client.get(
        '/lookup/activity-trackers/misc/', headers=test_client.staff_auth_header)

    assert response.status_code == 200
    assert response.json['total_items'] == 17
    assert len(response.json['items']) == 17
