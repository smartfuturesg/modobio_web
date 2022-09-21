import time

from flask.json import dumps
from sqlalchemy import delete, select

from odyssey.api.doctor.models import MedicalBloodTests, MedicalBloodTestResults
from .data import doctor_blood_tests_data, doctor_blood_tests_image_data
from tests.functional.user.data import users_staff_member_data

def test_post_medical_blood_test(test_client, care_team):
    # In this test:
    # - Make the same blood test entry from both the client and staff perspective.
    # - Staff must be added to the clinical care team of the client and be granted access.
    # - Test_ids are stored for use in tests later on

    global test_id_staff_submit, test_id_client_submit

    # Delete the current blood tests, if any.
    test_client.db.session.execute(delete(MedicalBloodTestResults))
    test_client.db.session.execute(delete(MedicalBloodTests))
    test_client.db.session.commit()

    ##
    # Submit blood test data as a client.
    ##
    response = test_client.post(
        f'/doctor/bloodtest/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(doctor_blood_tests_data),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['notes'] == 'test2'
    test_id_client_submit = response.json['test_id']

    ##
    # Submit the same blood test as an authorized staff.
    ##
    response = test_client.post(
        f'/doctor/bloodtest/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(doctor_blood_tests_data),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['notes'] == 'test2'
    test_id_staff_submit = response.json['test_id']

def test_get_client_blood_tests(test_client):
    # send get request for all client blood tests on user_id = client.user_id
    # sent as a logged-in staff member with authorization to view this client's blood tests
    response = test_client.get(
        f'/doctor/bloodtest/all/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['items'][0]['notes'] == 'test2'

def test_get_blood_test_results_all(test_client):
    # send get request for client info on user_id = client.user_id
    response = test_client.get(
        f'/doctor/bloodtest/results/all/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['test_results'] == 10
    assert response.json['items'][0]['results'][0]['modobio_test_code'] == 'TST003'
    assert response.json['items'][0]['results'][1]['modobio_test_code'] == 'HOR003'
    assert response.json['items'][0]['results'][2]['modobio_test_code'] == 'CMP010'
    assert response.json['items'][0]['results'][3]['modobio_test_code'] == 'CMP002'
    assert response.json['items'][0]['results'][4]['modobio_test_code'] == 'CMP001'

def test_get_blood_test_results(test_client):
    response = test_client.get(
        f'/doctor/bloodtest/results/{test_id_client_submit}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['items'][0]['results'][0]['evaluation'] == 'critical'
    assert response.json['items'][0]['results'][1]['evaluation'] == 'abnormal'
    assert response.json['items'][0]['results'][2]['evaluation'] == 'normal'
    assert response.json['items'][0]['results'][3]['evaluation'] == 'abnormal'
    assert response.json['items'][0]['results'][4]['evaluation'] == 'critical'
    assert response.json['items'][0]['reporter_id'] == test_client.client_id

    response = test_client.get(
        f'/doctor/bloodtest/results/{test_id_staff_submit}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['items'][0]['results'][0]['evaluation'] == 'critical'
    assert response.json['items'][0]['results'][1]['evaluation'] == 'abnormal'
    assert response.json['items'][0]['results'][2]['evaluation'] == 'normal'
    assert response.json['items'][0]['results'][3]['evaluation'] == 'abnormal'
    assert response.json['items'][0]['results'][4]['evaluation'] == 'critical'
    assert response.json['items'][0]['reporter_id'] == test_client.staff_id
    
def test_patch_blood_test_image(test_client):
    response = test_client.patch(
        f'/doctor/bloodtest/image/{test_client.client_id}/?test_id={test_id_client_submit}/',
        headers=test_client.client_auth_header,
        data=dumps(doctor_blood_tests_image_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    
    response = test_client.get(
        f'/doctor/bloodtest/image/{test_client.client_id}/?test_id={test_id_client_submit}/',
        headers=test_client.client_auth_header,
        content_type='application/json')
    
    assert response.status_code == 200
    assert response.json['image'] != None

def test_delete_blood_test(test_client):
    # send delete request where the user attempting to delete is not the reporter, should raise 401
    response = test_client.delete(
        f'/doctor/bloodtest/{test_client.client_id}/?test_id={test_id_staff_submit}',
        headers=test_client.client_auth_header)

    assert response.status_code == 401

    # send delete request for client blood test as the staff who did not submit the test
    response = test_client.delete(
        f'/doctor/bloodtest/{test_client.client_id}/?test_id={test_id_client_submit}',
        headers=test_client.staff_auth_header)

    assert response.status_code == 401

    # send delete request where the user attempting to delete is reporter
    response = test_client.delete(
        f'/doctor/bloodtest/{test_client.client_id}/?test_id={test_id_staff_submit}',
        headers=test_client.staff_auth_header)

    assert response.status_code == 204

    # send delete request for client blood test as the client who submitted the test
    response = test_client.delete(
        f'/doctor/bloodtest/{test_client.client_id}/?test_id={test_id_client_submit}',
        headers=test_client.client_auth_header)
    assert response.status_code == 204

    # send get request to ensure the test was deleted
    response = test_client.get(
        f'/doctor/bloodtest/results/{test_id_client_submit}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert not response.json

def test_get_bloodtest_search(test_client, blood_tests):
    """
    Test various scenarios for searching blood tests
    """

    # search for all blood tests by client id only
    # will return all blood tests in descending order by date
    response = test_client.get(
        f'/doctor/bloodtest/results/search/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['test_results'] == 2
    assert response.json['items'][0]['date'] > response.json['items'][1]['date']

    # search for all blood tests by client id and date range
    # will return one blood test
    response = test_client.get(
        f'/doctor/bloodtest/results/search/{test_client.client_id}/?start_date=2020-01-01&end_date=2020-01-02',\
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['test_results'] == 1

    # filter by test type
    response = test_client.get(
        f'/doctor/bloodtest/results/search/{test_client.client_id}/?modobio_test_code=CBC001',\
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['test_results'] == 1
    assert response.json['items'][0]['results'][0]['modobio_test_code'] == 'CBC001'


    # test pagination
    response = test_client.get(
        f'/doctor/bloodtest/results/search/{test_client.client_id}/?page=1&per_page=1',\
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['test_results'] == 1
    assert response.json['_links']['_next'] != None
    assert response.json['_links']['_prev'] == None
    
    # test pagination
    response = test_client.get(
        f'/doctor/bloodtest/results/search/{test_client.client_id}/?page=2&per_page=1',\
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['test_results'] == 1
    assert response.json['_links']['_prev'] != None
    assert response.json['_links']['_next'] == None