import time

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.doctor.models import MedicalHistory
from .data import doctor_medical_history_data

def test_post_medical_history(test_client):
    payload = doctor_medical_history_data

    response = test_client.post(
        f'/doctor/medicalhistory/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['concerns'] == doctor_medical_history_data['concerns']

def test_put_medical_history(test_client):
    doctor_medical_history_data['diagnostic_other'] = 'testing put'
    payload = doctor_medical_history_data

    response = test_client.put(
        f'/doctor/medicalhistory/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    client = MedicalHistory.query.filter_by(user_id=test_client.client_id).first()

    assert response.status_code == 200
    assert client.diagnostic_other == 'testing put'

def test_get_medical_history(test_client):
    response = test_client.get(
        f'/doctor/medicalhistory/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['concerns'] == doctor_medical_history_data['concerns']
    assert response.json['diagnostic_other'] == 'testing put'
