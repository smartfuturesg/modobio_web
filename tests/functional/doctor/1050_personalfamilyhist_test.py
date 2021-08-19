import time

from flask.json import dumps

from odyssey.api.doctor.models import MedicalHistory, MedicalFamilyHistory
from .data import doctor_personalfamilyhist_post_data, doctor_personalfamilyhist_put_data

def test_post_personalfamily_medical_history(test_client):
    payload = doctor_personalfamilyhist_post_data

    # send post request for client family history on user_id = 1
    response = test_client.post(
        f'/doctor/familyhistory/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    client_data = MedicalFamilyHistory.query.filter_by(user_id=test_client.client_id).all()

    assert response.status_code == 201
    assert response.json['total_items'] == 2
    assert len(response.json['items']) == 2
    assert len(client_data) == 2

    test = (MedicalFamilyHistory
        .query
        .filter_by(
            user_id=test_client.client_id,
            medical_condition_id=1)
        .one_or_none())

    assert test.myself == True

def test_put_personalfamily_medical_history(test_client):
    payload = doctor_personalfamilyhist_put_data

    # send put request for client family history on user_id = 1
    response = test_client.put(
        f'/doctor/familyhistory/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['total_items'] == 2
    assert len(response.json['items']) == 2

    test = (MedicalFamilyHistory
        .query
        .filter_by(
            user_id=test_client.client_id,
            medical_condition_id=1)
        .one_or_none())

    assert test.myself == False

def test_get_personalfamily_medical_history(test_client):
    response = test_client.get(
        f'/doctor/familyhistory/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['total_items'] == 3
    assert len(response.json['items']) == 3
