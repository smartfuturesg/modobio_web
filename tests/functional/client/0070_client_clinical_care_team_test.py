import base64

import pytest

from flask.json import dumps
from sqlalchemy import select

from odyssey.api.client.models import ClientClinicalCareTeam, ClientEHRPageAuthorizations
from odyssey.api.lookup.models import LookupEHRPages
from odyssey.api.user.models import User, UserLogin

from tests.functional.doctor.data import doctor_blood_tests_data
from tests.utils import login

NON_USER_TM = 'test_team_member_non_user@modobio.com'
USER_TM = 'test_team_member_user@modobio.com'

@pytest.fixture(scope='module')
def care_team(test_client):
    """ Add team members to client.
    
    Adds a team member who is staff and a team member who is client
    to the main testing client user. Additionally adds two team
    members who are not registered users.

    Returns
    -------
    dict
        Dictionary containing a client and a staff member from the
        database who were added to the care team of the main test
        client user. User_id and modobio_id for each are returned.
    """
    # Check that client emails don't already exist in database.
    emails = test_client.db.session.execute(select(User.email)).scalars().all()

    assert NON_USER_TM not in emails
    assert USER_TM not in emails

    # Staff user to be added as team member is our main test staff user.
    # There is currently only 1 client user in the seeded users, but that
    # is our main test client to whom we are adding team members. Create
    # a new client user here, who will be addded as a team member.
    tm_client = User(
        email = USER_TM,
        firstname = 'Team',
        lastname = 'Member',
        phone_number = '9871237766',
        modobio_id = 'ABC123X7Y8Z9',
        is_staff = False,
        is_client = True,
        email_verified = True)

    test_client.db.session.add(tm_client)
    test_client.db.session.commit()

    tm_login = UserLogin(user_id=tm_client.user_id)
    tm_login.set_password('password')

    test_client.db.session.add(tm_login)
    test_client.db.session.commit()    

    care_team = {
        'care_team': [
            {'team_member_email': NON_USER_TM},
            {'modobio_id': test_client.staff.modobio_id},
            {'modobio_id': tm_client.modobio_id}]}

    response = test_client.post(
        f'/client/clinical-care-team/members/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(care_team),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['total_items'] == 5
    assert response.json['care_team']

    # Find user_id for non-member user
    non_user_id = 0
    for member in response.json['care_team']:
        if member['team_member_email'] == NON_USER_TM:
            non_user_id = member['team_member_user_id']

    # Return user_id for new client and our staff user who are now in the care team.
    return {
        'staff_id': test_client.staff_id,
        'staff_modobio_id': test_client.staff.modobio_id,
        'client_id': tm_client.user_id,
        'client_modobio_id': tm_client.modobio_id,
        'non_user_id': non_user_id}

    # pro@modobio.com (10) and name@modobio.com (14) are already a care team members,
    # per database/1027_seed_users_ehr_auths.sql
    #
    # modobio_test=> select idx, "ClientClinicalCareTeam".user_id, team_member_user_id, "User".email from "ClientClinicalCareTeam" join "User" on team_member_user_id = "User".user_id;
    #
    #  idx | user_id | team_member_user_id |             email
    # -----+---------+---------------------+-------------------------------
    #    1 |      22 |                  10 | pro@modobio.com
    #    2 |      22 |                  14 | name@modobio.com
    #    3 |      22 |                  24 | test_team_member_non_user@modobio.com
    #    4 |      22 |                  12 | staff@modobio.com
    #    5 |      22 |                  23 | test_team_member_user@modobio.com

def test_adding_clinical_care_team(test_client, care_team):
    # check that the person added to the client's care team above sees the client
    # when viewing the list of clients whose care team they belong to
    response = test_client.get(
        '/client/clinical-care-team/member-of/{}/'.format(care_team['staff_id']),
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['member_of_care_teams'][0]['client_user_id'] == test_client.client_id

    ###
    # attempt to access /client/clinical-care-team/members/ as a staff member
    ###
    response = test_client.post(
        f'/client/clinical-care-team/members/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps({'care_team': [{'team_member_email': 'fail@modobio.com'}]}),
        content_type='application/json')

    assert response.status_code == 401

    ###
    # Attempt to add more than 20 clinical care team members
    ###
    long_care_team = {'care_team': [
        {'team_member_email': f'email{x:02d}@modobio.com'} for x in range(25)]}

    response = test_client.post(f'/client/clinical-care-team/members/{test_client.client_id}/',
                            headers=test_client.client_auth_header,
                            data=dumps(long_care_team),
                            content_type='application/json')

    assert response.status_code == 400

def test_delete_clinical_care_team(test_client, care_team):
    # Delete only the non-user team members: don't want to touch
    # team members added by database/1027_seed_users_ehr_auths.sql
    # add need the other two later.
    care_team_delete_payload = {
        'care_team': [{
            'team_member_user_id': care_team['non_user_id']}]}

    response = test_client.delete(
        f'/client/clinical-care-team/members/{test_client.client_id}/',
        data=dumps(care_team_delete_payload),
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200

def test_get_clinical_care_team(test_client, care_team):
    response = test_client.get(
        f'/client/clinical-care-team/members/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200

    # Was 5, deleted 1
    assert response.json['total_items'] == 4

def test_authorize_clinical_care_team(test_client, care_team):
    #####
    # Authorize another client to access all clinical care team resources
    #####
    total_resources = LookupEHRPages.query.count()
    auths = [{
        'team_member_user_id': care_team['client_id'],
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
        'team_member_user_id': care_team['staff_id'],
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
    # Try to authorize a resource that doesn't exist
    ####
    payload = {
        'ehr_page_authorizations': [{
            'team_member_user_id': care_team['client_id'],
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
    # As a staff member, post for data access.
    # Authorization should be pending.
    #####
    payload = {
        'ehr_page_authorizations': [{
            'team_member_user_id': care_team['staff_id'],
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
            ClientEHRPageAuthorizations.team_member_user_id == care_team['staff_id'],
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
        if (info['team_member_user_id'] == care_team['staff_id']
        and info['resource_group_id'] == total_resources):
            assert response.json['ehr_page_authorizations'][idx]['status'] == 'pending'

    # Now, note the header has switched to the test_client.client_auth_header, indicating
    # we are now the client of interest. We will now approve of this data access request.
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
        if info['team_member_user_id'] == care_team['staff_id']:
            assert response.json['ehr_page_authorizations'][idx]['status'] == 'accepted'

def test_clinical_care_team_access(test_client, care_team):
    # The intention of this test is to run through the authorization routine once,
    # rather than testing each endpoint that could be used by a care team member. 

    tm_client = test_client.db.session.query(User).get(care_team['client_id'])
    client_care_team_auth_header = login(test_client, tm_client)

    #####
    # Try to grab the blood tests and social history this client has submitted
    # 1. GET,POST from the client care perspective
    #    clients can view but cannot edit
    # 2. Try the same requests for the authorized staff
    #    POST request will succeed
    #####

    ###
    # as a clinical care team client
    ###
    response = test_client.get(
        f'/doctor/bloodtest/all/{test_client.client_id}/',
        headers=client_care_team_auth_header,
        content_type='application/json')

    # no content submitted yet but, sucessful request
    assert response.status_code == 204

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
