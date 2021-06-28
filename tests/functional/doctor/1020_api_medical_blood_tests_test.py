
import time 

from flask.json import dumps
from sqlalchemy import delete, select
from odyssey.api.client.models import ClientClinicalCareTeamAuthorizations
from odyssey.api.lookup.models import LookupClinicalCareTeamResources

from odyssey.api.user.models import User, UserLogin
from odyssey.api.doctor.models import MedicalBloodTests, MedicalBloodTestResults, MedicalBloodTestResultTypes
from .data import doctor_blood_tests_data
from tests.functional.user.data import users_staff_member_data


def test_post_medical_blood_test(test_client, init_database,  client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for medical blood test
    WHEN the '/doctor/bloodtest/<user_id>/' resource  is requested (POST)
        - make the same blood test entry from both the client and staff perspective
        - staff must be added to the clinical care team of the client and be granted access
        - test_ids are stored for use in tests later on 
    THEN check the response is valid
    """
    # save test_ids for following test routines
    global test_id_staff_submit, test_id_client_submit
    
    ##
    # give access to all clinical care team resources
    # delete previously assigned resources first
    ##
    clients_clinical_care_team = {'care_team' : [{'team_member_email': users_staff_member_data['email']}]}
    response = test_client.post(f"/client/clinical-care-team/members/{1}/",
                                data=dumps(clients_clinical_care_team),
                                headers=client_auth_header, 
                                content_type='application/json')

    total_resources = LookupClinicalCareTeamResources.query.count()
    auths = [{"team_member_user_id": 2,"resource_id": num} for num in range(1,total_resources+1) ]
    payload = {"clinical_care_team_authorization" : auths}
    response = test_client.post(f"/client/clinical-care-team/resource-authorization/{1}/",
                            headers=client_auth_header,
                            data=dumps(payload), 
                            content_type='application/json')

    # delete the current blood tests
    init_database.session.execute(delete(MedicalBloodTestResults))
    init_database.session.execute(delete(MedicalBloodTests))
    init_database.session.commit()

    ##
    # Submit blood test data as a client
    # send post request for client info on user_id = client.user_id
    ##
    response = test_client.post('/doctor/bloodtest/1/',
                                headers=client_auth_header, 
                                data=dumps(doctor_blood_tests_data), 
                                content_type='application/json')
    test_id_client_submit = response.json['test_id']
    assert response.status_code == 201
    assert response.json['panel_type'] == doctor_blood_tests_data['panel_type']

    ##
    # submit the same blood test as an authorized staff
    ##
    response = test_client.post('/doctor/bloodtest/1/',
                                headers=staff_auth_header, 
                                data=dumps(doctor_blood_tests_data), 
                                content_type='application/json')
    test_id_staff_submit = response.json['test_id']
    assert response.status_code == 201
    assert response.json['panel_type'] == doctor_blood_tests_data['panel_type']

def test_get_client_blood_tests(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for retrieving medical blood test instances
    WHEN the  '/doctor/bloodtest/all/<client id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    # send get request for all client blood tests on user_id = client.user_id
    # sent as a logged-in staff member with authorization to view this client's blood tests
    response = test_client.get('/doctor/bloodtest/all/1/',
                                headers=client_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200
    assert response.json['items'][0]['notes'] == 'test2'
    
def test_get_blood_test_results_all(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for retrieving medical blood tests results
    WHEN the  '/doctor/bloodtest/results/all/<test id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    # send get request for client info on user_id = client.user_id
    response = test_client.get('/doctor/bloodtest/results/all/1/',
                                headers=client_auth_header, 
                                content_type='application/json')
    assert response.status_code == 200
    assert response.json['test_results'] == 4
    assert response.json['items'][0]['panel_type'] == 'Lipids'

def test_get_blood_test_results(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for retrieving medical blood tests results
    WHEN the  '/doctor/bloodtest/results/<test id>/' resource  is requested (GET)
    THEN check the response is valid
    """
    # send get request for client info on user_id = client.user_id
    response = test_client.get(f'/doctor/bloodtest/results/{test_id_client_submit}/',
                                headers=client_auth_header, 
                                content_type='application/json')

    assert response.status_code == 200
    assert response.json['items'][0]['results'][0]['evaluation'] == 'optimal'
    assert response.json['items'][0]['results'][1]['evaluation'] == 'normal'
    assert response.json['items'][0]['reporter_id'] == 1

    # send get request for client info on user_id = client.user_id
    response = test_client.get(f'/doctor/bloodtest/results/{test_id_staff_submit}/',
                                headers=client_auth_header, 
                                content_type='application/json')

    assert response.status_code == 200
    assert response.json['items'][0]['results'][0]['evaluation'] == 'optimal'
    assert response.json['items'][0]['results'][1]['evaluation'] == 'normal'
    assert response.json['items'][0]['reporter_id'] == 2

def test_get_blood_test_result_types(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for retrieving medical blood tests result types
    WHEN the  '/bloodtest/result-types/' resource  is requested (GET)
    THEN check the response is valid
    """

    # send get request for client info on clientid = 1 
    response = test_client.get('doctor/bloodtest/result-types/',
                                headers=staff_auth_header, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    assert response.json['items'][0]['result_name'] == 'dihydroxyvitaminD'
    assert response.json['items'][0]['normal_max'] == 60

def test_delete_blood_test(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN an api end point for deleting a user's blood test results
    Testing delete request from:
        -staff who did/didnt submit result (pass/fail)
        -client who did/didnt submit result (pass/fail)
        -send get request to see if tests are still there
    WHEN the '/doctor/bloodtest/<user_id>/' resource is requested (DELETE)
    THEN check the response is valid
    """
    # send delete request where the user attempting to delete is not the reporter, should raise 401
    response = test_client.delete(f'/doctor/bloodtest/1/?test_id={test_id_staff_submit}',
                                headers=client_auth_header)
    assert response.status_code == 401

    # send delete request for client blood test as the staff who did not submit the test
    response = test_client.delete(f'/doctor/bloodtest/1/?test_id={test_id_client_submit}',
                                headers=staff_auth_header)
    assert response.status_code == 401

    # send delete request where the user attempting to delete is reporter
    response = test_client.delete(f'/doctor/bloodtest/1/?test_id={test_id_staff_submit}',
                                headers=staff_auth_header)
    assert response.status_code == 204

    # send delete request for client blood test as the client who submitted the test
    response = test_client.delete(f'/doctor/bloodtest/1/?test_id={test_id_client_submit}',
                                headers=client_auth_header)
    assert response.status_code == 204

    # repeat last request, fail 404
    response = test_client.delete(f'/doctor/bloodtest/1/?test_id={test_id_client_submit}',
                                headers=client_auth_header)

    assert response.status_code == 404

    # send get request to ensure the test was deleted
    response = test_client.get(f'/doctor/bloodtest/results/{test_id_client_submit}/',
                            headers=client_auth_header, 
                            content_type='application/json')

    assert response.status_code == 404