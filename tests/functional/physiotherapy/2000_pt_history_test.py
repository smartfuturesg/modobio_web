import time

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.physiotherapy.models import PTHistory
from .data import pt_history_data


def test_post_pt_history(test_client):
    payload = pt_history_data

    # For COVERAGE, raise a ContentNotFound error
    response = test_client.get(
        f'/physiotherapy/history/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')
    assert response.status_code == 204

    # For coverage, raise a UserNotFound error
    response = test_client.put(
        f'/physiotherapy/history/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 404

    response = test_client.post(
        f'/physiotherapy/history/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['exercise'] == pt_history_data['exercise']
    assert response.json['best_pain'] == pt_history_data['best_pain']

def test_put_pt_history(test_client):
    pt_history_data["exercise"] = "test put"
    payload = pt_history_data

    # For COVERAGE, raise an IllegalSettings Error
    response = test_client.post(
        f'/physiotherapy/history/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 400

    response = test_client.put(
        f'/physiotherapy/history/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    client = PTHistory.query.filter_by(user_id=test_client.client_id).first()

    assert response.status_code == 200
    assert client.exercise == "test put"

def test_get_pt_history(test_client):
    response = test_client.get(
        f'/physiotherapy/history/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['exercise'] == 'test put'
    assert response.json['best_pain'] == 7
