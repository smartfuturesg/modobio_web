import time

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.doctor.models import MedicalHistory
from .data import doctor_blood_pressures_data

def test_post_1_blood_pressure_history(test_client):
    # send post request for client blood pressure on user_id = 1
    response = test_client.post(
        '/doctor/bloodpressure/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(doctor_blood_pressures_data),
        content_type='application/json')

    assert response.status_code == 201

def test_get_1_blood_pressure_history(test_client):
    for header in (staff_auth_header, client_auth_header):
        # send get request for client blood pressure on user_id = 1
        response = test_client.get(
            f'/doctor/bloodpressure/{test_client.client_id}/',
            headers=header,
            content_type='application/json')

        assert response.status_code == 200
        assert len(response.json['items']) == 1
        assert response.json['total_items'] == 1

def test_delete_blood_pressure(test_client):
    # send delete request for client blood pressure on user_id = 1 and idx = 1
    response = test_client.delete(
        f'/doctor/bloodpressure/{test_client.client_id}/?idx=1',
        headers=test_client.client_auth_header)

    assert response.status_code == 204

    # send get request to ensure the result was deleted
    response = test_client.get(
        f'/doctor/bloodpressure/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert len(response.json['items']) == 0
    assert response.json['total_items'] == 0
