import base64

import pytest

from flask.json import dumps
from sqlalchemy import select

from odyssey.api.client.models import ClientClinicalCareTeamAuthorizations
from odyssey.api.lookup.models import LookupClinicalCareTeamResources
from odyssey.api.user.models import User
from odyssey.api.notifications.models import Notifications

from tests.functional.doctor.data import doctor_blood_tests_data
from tests.utils import login

def test_adding_clinical_care_team(test_client, care_team):
    # Care team is added in fixture. Check that staff member can see
    # that it is part of a care team.
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

    response = test_client.post(
        f'/client/clinical-care-team/members/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(long_care_team),
        content_type='application/json')

    assert response.status_code == 400

def test_delete_clinical_care_team(test_client, care_team):
    # Get members before
    response = test_client.get(
        f'/client/clinical-care-team/members/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    before = response.json['total_items']

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

    # Get members again check that 1 was deleted.
    response = test_client.get(
        f'/client/clinical-care-team/members/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['total_items'] == before - 1

def test_authorize_clinical_care_team(test_client, care_team):
    #####
    # Authorize another client to access all clinical care team resources
    #####
    total_resources = LookupClinicalCareTeamResources.query.count()
    auths = []
    for num in range(1, total_resources + 2):
        #must be length + 2 because id 4 was removed from the middle, making the count 1 less than the
        #highest index number
        #skip when num is 4 since that is the removed medications resource
        if num != 4:
            auths.append({
                'team_member_user_id': care_team['client_id'],
                'resource_id': num
            })
    payload = {'clinical_care_team_authorization': auths}

    response = test_client.post(
        f'/client/clinical-care-team/resource-authorization/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201

    #####
    # Authorize a staff to access all clinical care team resources
    # except the last one (used later on to make a request).
    #
    # care_team fixture already adds all authorizations for staff member,
    # so first delete them.
    #####
    cct_auths = (test_client.db.session.execute(
        select(ClientClinicalCareTeamAuthorizations)
        .filter_by(
            team_member_user_id=test_client.staff_id))
        .scalars()
        .all())

    for cct_auth in cct_auths:
        test_client.db.session.delete(cct_auth)
    test_client.db.session.commit()

    auths = []
    for num in range(1, total_resources + 2):
        #must be length + 2 because id 4 was removed from the middle, making the count 1 less than the
        #highest index number
        #skip when num is 4 since that is the removed medications resource
        if num != 4:
            auths.append({
                'team_member_user_id': care_team['staff_id'],
                'resource_id': num
            })
    payload = {'clinical_care_team_authorization': auths}

    response = test_client.post(
        f'/client/clinical-care-team/resource-authorization/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')
    breakpoint()
    print(response.data)
    assert response.status_code == 201

    #####
    # Try to authorize a resource that doesn't exist
    ####
    payload = {
        'clinical_care_team_authorization': [{
            'team_member_user_id': care_team['client_id'],
            'resource_id': 999999}]}

    response = test_client.post(
        f'/client/clinical-care-team/resource-authorization/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 400

    #####
    # Try to authorize a resource for a client not part of the care team that doesnt exist
    ####
    payload = {
        'clinical_care_team_authorization': [{
            'team_member_user_id': 99,
            'resource_id': 1}]}

    response = test_client.post(
        f'/client/clinical-care-team/resource-authorization/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 400

    #####
    # Get authorizations
    #####
    response = test_client.get(
        f'/client/clinical-care-team/resource-authorization/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['clinical_care_team_authorization'][0]['status'] == 'accepted'

    #####
    # As a staff member, post for data access.
    # Authorization should be pending.
    #####
    payload = {
        'clinical_care_team_authorization': [{
            'team_member_user_id': care_team['staff_id'],
            'resource_id': total_resources}]}

    response = test_client.post(
        f'/client/clinical-care-team/resource-authorization/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201

    staff_authorization = test_client.db.session.execute(
        select(ClientClinicalCareTeamAuthorizations)
        .filter(
            ClientClinicalCareTeamAuthorizations.team_member_user_id == care_team['staff_id'],
            ClientClinicalCareTeamAuthorizations.resource_id == total_resources)
        ).scalars().one_or_none()

    assert staff_authorization.status == 'pending'

    # Make a double post, expect an error
    response = test_client.post(
        f'/client/clinical-care-team/resource-authorization/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 400

    response = test_client.get(
        f'/client/clinical-care-team/resource-authorization/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['clinical_care_team_authorization'][0]['status'] == 'accepted'

    # The staff member requested data access of resource id = total_resources from user_id 1
    # The status was automatically set to 'pending'
    for idx, info in enumerate(response.json['clinical_care_team_authorization']):
        if (info['team_member_user_id'] == care_team['staff_id']
        and info['resource_id'] == total_resources):
            assert response.json['clinical_care_team_authorization'][idx]['status'] == 'pending'

    # Now, note the header has switched to the test_client.client_auth_header, indicating
    # we are now the client of interest. We will now approve of this data access request.
    response = test_client.put(
        f'/client/clinical-care-team/resource-authorization/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    response = test_client.get(
        f'/client/clinical-care-team/resource-authorization/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200

    for idx, info in enumerate(response.json['clinical_care_team_authorization']):
        if info['team_member_user_id'] == care_team['staff_id']:
            assert response.json['clinical_care_team_authorization'][idx]['status'] == 'accepted'

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
    assert response.status_code == 200

    response = test_client.get(
        f'/doctor/medicalinfo/social/{test_client.client_id}/',
        headers=client_care_team_auth_header,
        content_type='application/json')

    assert response.status_code == 200

    # try adding a blood treakest for this client
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

    assert response.status_code == 200

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
    assert response.json['notes'] == doctor_blood_tests_data['notes']

    #clean up notifications that were created from care team requests so they don't impact future tests
    notifications = Notifications.query.all()
    for notification in notifications:
        test_client.db.session.delete(notification)
    test_client.db.session.commit()