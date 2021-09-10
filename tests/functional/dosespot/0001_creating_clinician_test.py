import pytest
from copy import deepcopy
from flask.json import dumps
from odyssey import db
from odyssey.api.staff.models import StaffOffices
from tests.functional.staff.data import staff_office_data

# def test_post_1_ds_practitioner_create(test_client):
#     payload = {}
#     response = test_client.post(
#         f'/dosespot/create-practitioner/{test_client.staff_id}/',
#         headers=test_client.staff_auth_header,
#         data=dumps(payload),
#         content_type='application/json')
#     # Error because there has not been a StaffOffice yet
#     assert response.status_code == 406

# def test_post_1_create_staff_office(test_client):
#     payload = deepcopy(staff_office_data['normal_data'])
#     # phone number must not be sequential like 1234.. or repeating 1111.. etc
#     # phone number also must be 10 characters long
#     payload['phone'] = '6354523890'
#     response = test_client.post(f'/staff/offices/{test_client.staff_id}/',
#                                 headers=test_client.staff_auth_header,
#                                 data=dumps(payload),
#                                 content_type='application/json')
#     assert response.status_code == 201

# def test_post_2_ds_practitioner_create(test_client):
#     payload = {}
#     response = test_client.post(
#         f'/dosespot/create-practitioner/{test_client.staff_id}/',
#         headers=test_client.staff_auth_header,
#         data=dumps(payload),
#         content_type='application/json')

#     assert response.status_code == 201

# def test_post_1_ds_patient_prescribe(test_client):
#     payload = {}
#     response = test_client.post(
#         f'/dosespot/prescribe/{test_client.client_id}/',
#         headers=test_client.staff_auth_header,
#         data=dumps(payload),
#         content_type='application/json')

#     assert response.status_code == 201
#     global patient_sso
#     patient_sso = response.json

# def test_post_2_ds_patient_prescribe(test_client):
#     payload = {}
#     response = test_client.post(
#         f'/dosespot/prescribe/{test_client.client_id}/',
#         headers=test_client.staff_auth_header,
#         data=dumps(payload),
#         content_type='application/json')
    
#     assert response.status_code == 201
#     assert response.json == patient_sso

# def test_get_1_ds_practitioner_notification_sso(test_client):
#     response = test_client.get(f'/dosespot/notifications/{test_client.staff_id}/',
#                                 headers=test_client.staff_auth_header)

#     assert response.status_code == 200

# def test_delete_clean_staff_offices(test_client):
#     staff_office = StaffOffices.query.filter_by(user_id = test_client.staff_id).one_or_none()
#     db.session.delete(staff_office)
#     db.session.commit()