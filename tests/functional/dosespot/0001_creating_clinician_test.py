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

#     assert response.status_code == 200

# def test_get_ds_pharmacies(test_client):
#     response = test_client.get('/dosespot/pharmacies/',
#                                 headers=test_client.client_auth_header)
#     assert response.status_code == 201

# def test_get_patient_ds_pharmacies(test_client):
#     response = test_client.get(f'/dosespot/pharmacies/{test_client.client_id}/',
#                                 headers=test_client.client_auth_header)

#     assert response.status_code == 200

#TODO: Later problem
# def test_get_ds_patient_allergies(test_client):
#     response = test_client.get(f'/dosespot/allergies/{test_client.client_id}/',
#                                 headers=test_client.client_auth_header)

#     assert response.status_code == 200    

def test_get_select_ds_pharmacies(test_client):
    response = test_client.get(f'/dosespot/select/pharmacies/{test_client.client_id}/',
                                headers=test_client.client_auth_header)
    assert response.status_code == 200    
    assert len(response.json) == 100

def test_get_patient_ds_pharmacies(test_client):
    response = test_client.get(f'/dosespot/pharmacies/{test_client.client_id}/',
                                headers=test_client.client_auth_header)
    assert response.status_code == 200    

# def test_post_patient_ds_pharmacies(test_client):
#     payload = {'items':[{'pharmacy_id': 5},
#                         {'pharmacy_id': 276},
#                         {'pharmacy_id': 1000}]}

#     response = test_client.post(f'/dosespot/pharmacies/{test_client.client_id}/',
#                                 dumps=payload,
#                                 headers=test_client.client_auth_header)
#     breakpoint()
#     assert response.status_code == 200        

# def test_get_patient_ds_pharmacies(test_client):
#     response = test_client.get(f'/dosespot/pharmacies/{test_client.client_id}/',
#                                 headers=test_client.client_auth_header)
#     breakpoint()
    
#     assert response.status_code == 200 
#     assert len(response.json) == 3   