import pytest

from flask.json import dumps

from odyssey.api.facility.models import MedicalInstitutions

# from .data import doctor_clients_external_medical_records_data



def test_post_1_ds_practitioner_create(test_client):
    payload = {}
    response = test_client.post(
        f'/dosespot/create-practioner/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')
    assert response.status_code == 201

def test_post_1_ds_patient_prescribe(test_client):
    payload = {}
    response = test_client.post(
        f'/dosespot/prescribe/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201
    global patient_sso
    patient_sso = response.json

def test_post_2_ds_patient_prescribe(test_client):
    payload = {}
    response = test_client.post(
        f'/dosespot/prescribe/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')
    
    assert response.status_code == 201
    assert response.json == patient_sso

def test_get_1_ds_practitioner_notification_sso(test_client):
    response = test_client.get(f'/dosespot/notifications/{test_client.staff_id}/',
                                headers=test_client.staff_auth_header)

    assert response.status_code == 200
    