from flask.json import dumps

from .data import (
    doctor_all_socialhistory_post_1_data,
    doctor_all_socialhistory_post_2_data,
    doctor_all_socialhistory_post_3_data,
    doctor_all_socialhistory_break_post_1_data,
    doctor_all_socialhistory_break_post_2_data)

def test_get_std_conditions(test_client):
    response = test_client.get(
        '/doctor/lookupstd/',
        headers=test_client.client_auth_header)

    assert response.status_code == 200
    assert response.json['total_items'] == 22
    assert len(response.json['items']) == 22

def test_post_1_social_history(test_client):
    payload = doctor_all_socialhistory_post_1_data

    response = test_client.post(
        f'/doctor/medicalinfo/social/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201

def test_get_social_medical_history(test_client):
    response = test_client.get(
        f'/doctor/medicalinfo/social/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert len(response.json['std_history']) == 3
    assert response.json['social_history']['currently_smoke'] == True

def test_post_2_social_history(test_client):
    payload = doctor_all_socialhistory_post_2_data

    # send put request for client social history on user_id = 1
    response = test_client.post(
        f'/doctor/medicalinfo/social/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201

def test_get_2_social_medical_history(test_client):
    response = test_client.get(
        f'/doctor/medicalinfo/social/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert len(response.json['std_history']) == 1
    assert response.json['social_history']['currently_smoke'] == False

def test_break_post_1_social_history(test_client):
    payload = doctor_all_socialhistory_break_post_1_data

    response = test_client.post(
        f'/doctor/medicalinfo/social/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    # Currently smoke is false, and do not provide last_smoke (int)
    assert response.status_code == 400

def test_get_broke_1_social_medical_history(test_client):
    response = test_client.get(
        f'/doctor/medicalinfo/social/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert len(response.json['std_history']) == 1
    assert response.json['social_history']['currently_smoke'] == False

def test_break_post_2_social_history(test_client):
    payload = doctor_all_socialhistory_break_post_2_data

    # send put request for client social history on user_id = 1
    response = test_client.post(
        f'/doctor/medicalinfo/social/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    # STD lookup out of range
    assert response.status_code == 400

def test_get_broke_2_social_medical_history(test_client):
    response = test_client.get(
        f'/doctor/medicalinfo/social/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert len(response.json['std_history']) == 1
    assert response.json['social_history']['currently_smoke'] == False

# NRV 1577, FE Bug
def test_post_3_social_history(test_client):
    payload = doctor_all_socialhistory_post_3_data

    response = test_client.post(
        f'/doctor/medicalinfo/social/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201

def test_get_3_social_medical_history(test_client):
    response = test_client.get(
        f'/doctor/medicalinfo/social/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['social_history']['currently_smoke'] == False
