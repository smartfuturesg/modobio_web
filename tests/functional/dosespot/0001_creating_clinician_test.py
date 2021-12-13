import pytest
from copy import deepcopy
from flask.json import dumps
from odyssey import db
from odyssey.api.staff.models import StaffOffices
from tests.functional.staff.data import staff_office_data

def test_get_select_ds_pharmacies(test_client):
    response = test_client.get(f'/dosespot/select/pharmacies/{test_client.client_id}/',
                                headers=test_client.client_auth_header)

    assert response.status_code == 200    
    assert len(response.json) == 100

def test_post_patient_ds_pharmacies(test_client):
    payload = {'items':[{'pharmacy_id': 5,
                         'primary_pharm': False},
                        {'pharmacy_id': 276,
                         'primary_pharm': False},
                        {'pharmacy_id': 1000,
                         'primary_pharm': True}]}

    response = test_client.post(f'/dosespot/pharmacies/{test_client.client_id}/',
                                data=dumps(payload),
                                headers=test_client.client_auth_header,
                                content_type='application/json')
    
    # Note, pharmacy_id 5 is invalid, but is still able to proceed to post
    assert response.status_code == 201   

def test_get_patient_ds_pharmacies(test_client):
    response = test_client.get(f'/dosespot/pharmacies/{test_client.client_id}/',
                                headers=test_client.client_auth_header)
    assert response.status_code == 200 
    assert len(response.json) == 2  

def test_post_patient_prescription(test_client):
    response = test_client.post(f'/dosespot/prescribe/{test_client.client_id}/',
                                headers=test_client.staff_auth_header)
    assert response.status_code == 201

def test_get_patient_ds_prescriptions(test_client):
    response = test_client.get(f'/dosespot/prescribe/{test_client.client_id}/',
                                headers=test_client.client_auth_header)

    assert response.status_code == 200 


