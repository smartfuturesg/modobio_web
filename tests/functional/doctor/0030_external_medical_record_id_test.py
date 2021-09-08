import pytest

from flask.json import dumps

from odyssey.api.facility.models import MedicalInstitutions

from .data import doctor_clients_external_medical_records_data

# Add medical institutes, only used in the tests in this file
@pytest.fixture(scope='module', autouse=True)
def add_institutions(test_client):
    mi1 = MedicalInstitutions(institute_name='Mercy Gilbert Medical Center')
    mi2 = MedicalInstitutions(institute_name='Mercy Tempe Medical Center')
    test_client.db.session.add_all([mi1, mi2])
    test_client.db.session.commit()

def test_post_medical_record_ids(test_client):
    payload = doctor_clients_external_medical_records_data

    response = test_client.post(
        f'/doctor/medicalinstitutions/recordid/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['record_locators'][0]['med_record_id'] == doctor_clients_external_medical_records_data['record_locators'][0]['med_record_id']

def test_get_medical_record_ids(test_client):
    response = test_client.get(
        f'/doctor/medicalinstitutions/recordid/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['record_locators'][0]['med_record_id'] == doctor_clients_external_medical_records_data['record_locators'][0]['med_record_id']

def test_get_medical_institutes(test_client):
    response = test_client.get(
        '/doctor/medicalinstitutions/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json[0]['institute_name'] == 'Mercy Gilbert Medical Center'
