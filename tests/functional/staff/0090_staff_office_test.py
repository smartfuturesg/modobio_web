from flask import current_app
from .data import staff_office_data
from flask.json import dumps
from odyssey.api.dosespot.models import DoseSpotPractitionerID

def test_post_staff_office(test_client):
    #test with invalid territory id, should return 400
    response = test_client.post(f'/staff/offices/{test_client.staff_id}/',
                                headers=test_client.staff_auth_header,
                                data=dumps(staff_office_data['invalid_territory_id']),
                                content_type='application/json')

    # some simple checks for validity
    assert response.status_code == 400

    #test with invalid state id, should return 400
    response = test_client.post(f'/staff/offices/{test_client.staff_id}/',
                                headers=test_client.staff_auth_header,
                                data=dumps(staff_office_data['invalid_state_id']),
                                content_type='application/json')

    # some simple checks for validity
    assert response.status_code == 400

    #test with a field that exceeds its maximum length, should return 400
    response = test_client.post(f'/staff/offices/{test_client.staff_id}/',
                                headers=test_client.staff_auth_header,
                                data=dumps(staff_office_data['too_long']),
                                content_type='application/json')

    # some simple checks for validity
    assert response.status_code == 400

    #test with invalid phone type, should return 404
    response = test_client.post(f'/staff/offices/{test_client.staff_id}/',
                                headers=test_client.staff_auth_header,
                                data=dumps(staff_office_data['invalid_phone_type']),
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 400

    #test with valid data, should return 201
    response = test_client.post(f'/staff/offices/{test_client.staff_id}/',
                                headers=test_client.staff_auth_header,
                                data=dumps(staff_office_data['normal_data']),
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 201
    assert response.json['country'] == 'USA'
    assert response.json['city'] == 'Miami'
    assert response.json['phone'] == '4804389574'
    assert response.json['state_id'] == 9

    # # There is a Database listener waiting for both medical credentials and staff office.
    # # Once those are done, the system will automatically try to onboard the practitioner.
    # ds_practitioner = DoseSpotPractitionerID.query.filter_by(user_id=test_client.staff_id).one_or_none()
    # assert ds_practitioner != None

def test_post_2_ds_practitioner_create(test_client):
    payload = {}
    response = test_client.post(
        f'/dosespot/create-practitioner/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201

def test_get_1_ds_practitioner_notification_sso(test_client):
    response = test_client.get(f'/dosespot/notifications/{test_client.staff_id}/',
                                headers=test_client.staff_auth_header)
    assert response.status_code == 200

def test_get_staff_office(test_client):
    response = test_client.get(f'/staff/offices/{test_client.staff_id}/',
                                headers=test_client.staff_auth_header)
    
    # some simple checks for validity
    assert response.status_code == 200
    assert response.json['country'] == 'USA'
    assert response.json['phone'] == '4804389574'

def test_put_staff_profile(test_client):
    #test with invalid country id, should return 400
    response = test_client.put(f'/staff/offices/{test_client.staff_id}/',
                                headers=test_client.staff_auth_header,
                                data=dumps(staff_office_data['invalid_territory_id']),
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 400

    #test with a field that exceeds its maximum length, should return 400
    response = test_client.put(f'/staff/offices/{test_client.staff_id}/',
                                headers=test_client.staff_auth_header,
                                data=dumps(staff_office_data['too_long']),
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 400

    #test with invalid country id, should return 404
    response = test_client.put(f'/staff/offices/{test_client.staff_id}/',
                                headers=test_client.staff_auth_header,
                                data=dumps(staff_office_data['invalid_phone_type']),
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 400

    #test with valid data, should return 201
    response = test_client.put(f'/staff/offices/{test_client.staff_id}/',
                                headers=test_client.staff_auth_header,
                                data=dumps(staff_office_data['normal_data_2']),
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 201
    assert response.json['country'] == 'USA'
    assert response.json['city'] == 'Tampa'
    assert response.json['phone'] == '4804389575'
    assert response.json['state_id'] == 9

def test_post_2_ds_practitioner_create(test_client):
    payload = {}
    response = test_client.post(
        f'/dosespot/create-practitioner/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    # This user should already be in the DS system
    assert response.status_code == 400

def test_post_1_ds_patient_prescribe(test_client):
    payload = {}
    response = test_client.post(
        f'/dosespot/prescribe/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201
    global patient_sso
    patient_sso = response.json['url']
    

def test_post_2_ds_patient_prescribe(test_client):
    payload = {}
    response = test_client.post(
        f'/dosespot/prescribe/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')
    
    assert response.status_code == 201
    assert response.json['url'] == patient_sso

def test_get_1_ds_practitioner_notification_sso(test_client):
    response = test_client.get(f'/dosespot/notifications/{test_client.staff_id}/',
                                headers=test_client.staff_auth_header)
    assert response.status_code == 200