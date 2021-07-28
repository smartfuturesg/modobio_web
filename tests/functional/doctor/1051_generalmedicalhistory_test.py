import time

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.doctor.models import MedicalHistory, MedicalGeneralInfo
from .data import (
    doctor_medicalgeneralinfo_post_data,
    doctor_medicalgeneralinfo_put_data,
    doctor_medicalmedicationsinfo_post_data,
    doctor_medicalmedicationsinfo_put_data,
    doctor_medicalmedicationsinfo_delete_data,
    doctor_medicalallergiesinfo_post_data,
    doctor_medicalallergiesinfo_put_data,
    doctor_medicalallergiesinfo_delete_data
)

def test_post_general_medical_history(test_client):
    payload = doctor_medicalgeneralinfo_post_data

    # send post request for client general medical history on user_id = 1
    response = test_client.post(
        f'/doctor/medicalinfo/general/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['primary_doctor_contact_name'] == 'Dr Guy'

def test_put_general_medical_history(test_client):
    payload = doctor_medicalgeneralinfo_put_data

    # send put request for client general medical history on user_id = 1
    response = test_client.put(
        f'/doctor/medicalinfo/general/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    client_data = (MedicalGeneralInfo
        .query
        .filter_by(user_id=test_client.client_id)
        .one_or_none())

    assert response.status_code == 201
    assert response.json['primary_doctor_contact_name'] == 'Dr Steve'
    assert client_data.primary_doctor_contact_name == 'Dr Steve'

def test_get_general_medical_history(test_client):
    for header in (staff_auth_header, client_auth_header):
        # send get request for client general medical history on user_id = 1
        response = test_client.get(
            f'/doctor/medicalinfo/general/{test_client.client_id}/',
            headers=header,
            content_type='application/json')

        assert response.status_code == 200
        assert response.json['primary_doctor_contact_name'] == 'Dr Steve'

################ TEST MEDICATION HISTORY ####################

def test_post_medication_medical_history(test_client):
    payload = doctor_medicalmedicationsinfo_post_data

    # send post request for client medication history on user_id = 1
    response = test_client.post(
        f'/doctor/medicalinfo/medications/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['medications'][0]['medication_name'] == 'medName1'
    assert len(response.json['medications']) == 2

def test_put_medication_medical_history(test_client):
    payload = doctor_medicalmedicationsinfo_put_data

    # send put request for client medication history on user_id = 1
    response = test_client.put(
        f'/doctor/medicalinfo/medications/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['medications'][0]['medication_name'] == 'medName4'
    assert len(response.json['medications']) == 2

def test_get_medication_medical_history(test_client):
    for header in (staff_auth_header, client_auth_header):
        # send get request for client medication history on user_id = 1
        response = test_client.get(
            f'/doctor/medicalinfo/medications/{test_client.client_id}/',
            headers=header,
            content_type='application/json')

        assert response.status_code == 200
        assert response.json['medications'][0]['medication_name'] == 'medName4'
        assert len(response.json['medications']) == 2

def test_delete_medication_medical_history(test_client):
    payload = doctor_medicalmedicationsinfo_delete_data

    response = test_client.delete(
        f'/doctor/medicalinfo/allergies/{test_client.client_id}/',
        data=dumps(payload),
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 201

def test_get_medication_medical_history_after_delete(test_client):
    for header in (staff_auth_header, client_auth_header):
        # send get request for client medication history on user_id = 1
        response = test_client.get(
            f'/doctor/medicalinfo/medications/{test_client.client_id}/',
            headers=header,
            content_type='application/json')

        assert response.status_code == 200
        assert len(response.json['medications']) == 2

################ TEST ALLERGY HISTORY ####################

def test_post_allergy_medical_history(test_client):
    payload = doctor_medicalallergiesinfo_post_data

    # send post request for client medication allergy history on user_id = 1
    response = test_client.post(
        f'/doctor/medicalinfo/allergies/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['allergies'][0]['medication_name'] == 'medName3'
    assert len(response.json['allergies']) == 3

def test_put_allergy_medical_history(test_client):
    payload = doctor_medicalallergiesinfo_put_data

    # send put request for client medication allergy history on user_id = 1
    response = test_client.put(
        f'/doctor/medicalinfo/allergies/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['allergies'][0]['medication_name'] == 'medName4'
    assert len(response.json['allergies']) == 1

def test_get_allergy_medical_history(test_client):
    for header in (staff_auth_header, client_auth_header):
        # send get request for client medication allergy history on user_id = 1
        response = test_client.get(
            f'/doctor/medicalinfo/allergies/{test_client.client_id}/',
            headers=header,
            content_type='application/json')

        assert response.status_code == 200
        assert len(response.json['allergies']) == 3

def test_delete_allergy_medical_history(test_client):
    payload = doctor_medicalallergiesinfo_delete_data

    response = test_client.delete(
        f'/doctor/medicalinfo/allergies/{test_client.client_id}/',
        data=dumps(payload),
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 201

def test_get_allergy_medical_history_after_delete(test_client):
    for header in (staff_auth_header, client_auth_header):
        # send get request for client medication allergy history on user_id = 1
        response = test_client.get(
            f'/doctor/medicalinfo/allergies/{test_client.client_id}/',
            headers=header,
            content_type='application/json')

        assert response.status_code == 200
        assert len(response.json['allergies']) == 2
