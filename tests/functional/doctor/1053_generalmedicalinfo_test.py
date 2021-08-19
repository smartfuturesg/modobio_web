import time

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.doctor.models import MedicalHistory
from .data import (
    doctor_all_generalmedicalinfo_post_1_data,
    doctor_all_generalmedicalinfo_post_2_data,
    doctor_all_generalmedicalinfo_post_3_data,
    doctor_all_generalmedicalinfo_post_4_data,
    doctor_all_generalmedicalinfo_post_5_data)

def test_post_1_general_medical_history(test_client):
    payload = doctor_all_generalmedicalinfo_post_1_data

    response = test_client.post(
        f'/doctor/medicalgeneralinfo/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201

def test_get_1_general_medical_history(test_client):
    response = test_client.get(
        f'/doctor/medicalgeneralinfo/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['gen_info']['primary_doctor_contact_name'] == 'Dr Guy'
    assert len(response.json['medications']) == 2
    assert len(response.json['allergies']) == 3

def test_post_2_general_medical_history(test_client):
    payload = doctor_all_generalmedicalinfo_post_2_data

    response = test_client.post(
        f'/doctor/medicalgeneralinfo/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201

def test_get_2_general_medical_history(test_client):
    response = test_client.get(
        f'/doctor/medicalgeneralinfo/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['gen_info']['primary_doctor_contact_name'] == 'Dr Steve'
    assert len(response.json['medications']) == 3
    assert len(response.json['allergies']) == 1

def test_post_3_general_medical_history(test_client):
    payload = doctor_all_generalmedicalinfo_post_3_data

    response = test_client.post(
        f'/doctor/medicalgeneralinfo/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    # should produce an error
    assert response.status_code == 405

def test_get_3_general_medical_history(test_client):
    response = test_client.get(
        f'/doctor/medicalgeneralinfo/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    # previous POST request produced an error,
    # GET request should return the same as GET test 2
    assert response.status_code == 200
    assert response.json['gen_info']['primary_doctor_contact_name'] == 'Dr Steve'
    assert len(response.json['medications']) == 3
    assert len(response.json['allergies']) == 1

def test_post_4_general_medical_history(test_client):
    payload = doctor_all_generalmedicalinfo_post_4_data

    response = test_client.post(
        f'/doctor/medicalgeneralinfo/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201

def test_get_4_general_medical_history(test_client):
    response = test_client.get(
        f'/doctor/medicalgeneralinfo/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    # Remove medications from payload, so the get request
    # should expect no medication history in it.
    assert response.status_code == 200
    assert response.json['gen_info']['primary_doctor_contact_name'] == 'Dr Dude'
    assert len(response.json['medications']) == 0
    assert len(response.json['allergies']) == 1

def test_post_5_general_medical_history(test_client):
    payload = doctor_all_generalmedicalinfo_post_5_data

    response = test_client.post(
        f'/doctor/medicalgeneralinfo/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    # Post an invalid request,
    # allergies field missing medication name.
    assert response.status_code == 405

def test_get_5_general_medical_history(test_client):
    response = test_client.get(
        f'/doctor/medicalgeneralinfo/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    # Removed General Info from payload BUT
    # also removed medication name from allergies, so we should expect
    # a DB rollback, and the GET request should be the same as test 4
    assert response.status_code == 200
    assert response.json['gen_info']['primary_doctor_contact_name'] == 'Dr Dude'
    assert len(response.json['medications']) == 0
    assert len(response.json['allergies']) == 1
