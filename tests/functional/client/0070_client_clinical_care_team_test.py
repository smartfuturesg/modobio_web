import base64

from flask.json import dumps
from flask_accepts.decorators.decorators import responds
from sqlalchemy import select

from odyssey.api.client.models import ClientEHRPageAuthorizations
from odyssey.api.lookup.models import LookupEHRPages
from odyssey.api.user.models import User

from tests.functional.client.data import clients_clinical_care_team
from tests.functional.user.data import users_new_user_client_data
from tests.functional.doctor.data import doctor_blood_tests_data

def test_adding_clinical_care_team(test_client):
    global team_member_staff_user_id, team_member_staff_modobio_id, team_member_client_user_id, team_member_client_modobio_id

    current_user_emails = test_client.db.session.execute(select(User.email)).scalars().all()
    care_team_add_emails = [x['team_member_email'] for x in clients_clinical_care_team['care_team']]

    # care team members being added are not current users
    assert len(set(current_user_emails) - set(care_team_add_emails)) == len(current_user_emails)

    team_member_staff_modobio_id, team_member_staff_user_id = test_client.db.session.execute(
        select(User.modobio_id, User.user_id)
        .filter(User.is_staff == True)
        ).first()

    team_member_client_modobio_id, team_member_client_user_id = test_client.db.session.execute(
        select(User.modobio_id, User.user_id)
        .filter(
            User.email == 'name@modobio.com')
        ).one_or_none()

    clients_clinical_care_team['care_team'].extend([
        {'modobio_id': team_member_staff_modobio_id},
        {'modobio_id': team_member_client_modobio_id}])

    response = test_client.post(
        f'/client/clinical-care-team/members/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(clients_clinical_care_team),
        content_type='application/json')

    current_user_emails_updated = test_client.db.session.execute(select(User.email)).scalars().all()

    assert response.status_code == 201
    # pro@modobio.com is already a care team member, per 1026_add_care_team_resources.sql
    assert response.json.get('total_items') == 5
    assert response.json.get('care_team')
    # ensure users were added through the care team system
    assert len(set(current_user_emails_updated) - set(current_user_emails) ) == len(care_team_add_emails)

    #check that the person added to the client's care team above sees the client
    #when viewing the list of clients whose care team they belong to
    response = test_client.get(
        f'/client/clinical-care-team/member-of/{team_member_staff_user_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    # TODO: 401 unauthorized
    assert response.status_code == 200
    assert response.json['member_of_care_teams'][0]['client_user_id'] == 1

    ###
    # attempt to access /client/clinical-care-team/members/ as a staff member
    ###
    response = test_client.post(
        f'/client/clinical-care-team/members/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(clients_clinical_care_team),
        content_type='application/json')

    assert response.status_code == 401

    ###
    # Attempt to add more than 20 clinical care team members
    ###
    clients_clinical_care_team['care_team'].extend([
        {'team_member_email': 'email1@modo.com'},
        {'team_member_email': 'email2@modo.com'},
        {'team_member_email': 'email3@modo.com'},
        {'team_member_email': 'email4@modo.com'},
        {'team_member_email': 'email5@modo.com'},
        {'team_member_email': 'email6@modo.com'},
        {'team_member_email': 'email7@modo.com'},
        {'team_member_email': 'email8@modo.com'},
        {'team_member_email': 'email9@modo.com'},
        {'team_member_email': 'email10@modo.com'},
        {'team_member_email': 'email12@modo.com'},
        {'team_member_email': 'email13@modo.com'},
        {'team_member_email': 'email14@modo.com'},
        {'team_member_email': 'email15@modo.com'},
        {'team_member_email': 'email16@modo.com'},
        {'team_member_email': 'email17@modo.com'},
        {'team_member_email': 'email18@modo.com'},
        {'team_member_email': 'email19@modo.com'}])

    response = test_client.post(f'/client/clinical-care-team/members/{test_client.client_id}/',
                            headers=test_client.client_auth_header,
                            data=dumps(clients_clinical_care_team),
                            content_type='application/json')

    assert response.status_code == 400

def test_delete_clinical_care_team(test_client):
    # keep these users in the care team
    clients_clinical_care_team['care_team'].remove({'modobio_id': team_member_staff_modobio_id})
    clients_clinical_care_team['care_team'].remove({'modobio_id': team_member_client_modobio_id})

    response = test_client.delete(
        f'/client/clinical-care-team/members/{test_client.client_id}/',
        data=dumps(clients_clinical_care_team),
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200

def test_get_clinical_care_team(test_client):
    response = test_client.get(
        f'/client/clinical-care-team/members/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json.get('total_items') == 5

def test_authorize_clinical_care_team(test_client):
    #####
    # Authorize another client to access all clinical care team resources
    #####
    total_resources = LookupEHRPages.query.count()
    auths = [{
        'team_member_user_id': team_member_client_user_id,
        'resource_group_id': num}
        for num in range(1, total_resources + 1)]
    payload = {'ehr_page_authorizations': auths}

    response = test_client.post(
        f'/client/clinical-care-team/ehr-page-authorization/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201

    #####
    # Authorize a staff to access all clinical care team resources but the last one (used later on to make a request)
    #####
    auths = [{
        'team_member_user_id': team_member_staff_user_id,
        'resource_group_id': num}
        for num in range(1, total_resources)]
    payload = {'ehr_page_authorizations': auths}

    response = test_client.post(
        f'/client/clinical-care-team/ehr-page-authorization/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201

    #####
    # Try to authorize a resource that doesnt exist
    ####
    payload = {
        'ehr_page_authorizations': [{
            'team_member_user_id': team_member_client_user_id,
            'resource_group_id': 999999}]}

    response = test_client.post(
        f'/client/clinical-care-team/ehr-page-authorization/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 400

    #####
    # Try to authorize a resource for a client not part of the care team that doesnt exist
    ####
    payload = {
        'ehr_page_authorizations': [{
            'team_member_user_id': 99,
            'resource_group_id': 1}]}

    response = test_client.post(
        f'/client/clinical-care-team/ehr-page-authorization/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 400

    #####
    # Get authorizations
    #####
    response = test_client.get(
        f'/client/clinical-care-team/ehr-page-authorization/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['ehr_page_authorizations'][0]['status'] == 'accepted'

    #####
    # as a staff member, post for data access.
    # authorization should be pending
    #####
    # Create payload for team_member_user_id 2 (a staff member)
    payload = {
        'ehr_page_authorizations': [{
            'team_member_user_id': team_member_staff_user_id,
            'resource_group_id': total_resources}]}

    response = test_client.post(
        f'/client/clinical-care-team/ehr-page-authorization/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201

    staff_authorization = test_client.db.session.execute(
        select(ClientEHRPageAuthorizations)
        .filter(
            ClientEHRPageAuthorizations.team_member_user_id == team_member_staff_user_id,
            ClientEHRPageAuthorizations.resource_group_id == total_resources)
        ).scalars().one_or_none()

    assert staff_authorization.status == 'pending'

    # Make a double post, expect an error
    response = test_client.post(
        f'/client/clinical-care-team/ehr-page-authorization/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 400

    response = test_client.get(
        f'/client/clinical-care-team/ehr-page-authorization/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['ehr_page_authorizations'][0]['status'] == 'accepted'

    # The staff member requested data access of resource id = total_resources from user_id 1
    # The status was automatically set to 'pending'
    for idx, info in enumerate(response.json['ehr_page_authorizations']):
        if (info['team_member_email'] == 'staff_member@modobio.com'
        and info['resource_group_id'] == total_resources):
            assert response.json['ehr_page_authorizations'][idx]['status'] == 'pending'

    # Now, note the header has switched to the test_client.client_auth_header indicating we are now the client of interest
    # We will now approve of this data access request.
    response = test_client.put(
        f'/client/clinical-care-team/ehr-page-authorization/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    response = test_client.get(
        f'/client/clinical-care-team/ehr-page-authorization/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200

    for idx, info in enumerate(response.json['ehr_page_authorizations']):
        if info['team_member_email'] == 'staff_member@modobio.com':
            assert response.json['ehr_page_authorizations'][idx]['status'] == 'accepted'

def test_clinical_care_team_access(test_client):
    valid_credentials = base64.b64encode('name@modobio.com:123'.encode('utf-8')).decode('utf-8')

    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post(
        '/client/token/',
        headers=headers,
        content_type='application/json')

    token = response.json.get('token')
    client_care_team_auth_header = {'Authorization': f'Bearer {token}'}

    #####
    # Try to grab the blood tests and social history this client has submitted
    # 1. GET,POST from the client care perspective
    #   clients can view but cannot edit
    # 2. Try the same requests for the authorized staff
    #   POST request will succeed
    #####

    ###
    # as a clinical care team client
    ###
    response = test_client.get(
        f'/doctor/bloodtest/all/{test_client.client_id}/',
        headers=client_care_team_auth_header,
        content_type='application/json')

    assert response.status_code == 204 # no content submitted yet but, sucessful request

    response = test_client.get(
        f'/doctor/medicalinfo/social/{test_client.client_id}/',
        headers=client_care_team_auth_header,
        content_type='application/json')

    assert response.status_code == 200

    # try adding a blood test for this client
    response = test_client.post(
        f'/doctor/bloodtest/{test_client.client_id}/',
        headers=client_care_team_auth_header,
        data=dumps(doctor_blood_tests_data),
        content_type='application/json')

    assert response.status_code == 401

    ###
    # as a clinical care team staff
    ###
    response = test_client.get(
        f'/doctor/bloodtest/all/{test_client.client_id}/',
        headers=client_care_team_auth_header,
        content_type='application/json')

    assert response.status_code == 204 # no content submitted yet but, sucessful request

    response = test_client.get(
        f'/doctor/medicalinfo/social/{test_client.client_id}/',
        headers=client_care_team_auth_header,
        content_type='application/json')

    assert response.status_code == 200

    # try adding a blood test for this client
    response = test_client.post(
        f'/doctor/bloodtest/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(doctor_blood_tests_data),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['panel_type'] == doctor_blood_tests_data['panel_type']
