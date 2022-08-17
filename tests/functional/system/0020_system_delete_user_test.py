import base64

from flask.json import dumps
from sqlalchemy import select, text
from odyssey.api.lookup.models import LookupClinicalCareTeamResources

from odyssey.api.user.models import User, UserLogin, UserRemovalRequests, UserPendingEmailVerifications
from odyssey.api.doctor.models import MedicalImaging
from tests.functional.user.data import users_to_delete_data
from tests.functional.doctor.data import doctor_medical_imaging_data
from tests.functional.client.data import client_profile_picture_data
from tests.utils import login

def test_account_delete_client_and_staff(test_client):
    #Create a new staff user and a new client user
    #1. Create self created client user
    payload = users_to_delete_data['client_user']
    client_user = test_client.post(
        '/user/client/',
        data=dumps(payload),
        content_type='application/json')
    client_id = client_user.json['user_info']['user_id']

    #verify newly created client's email
    token = UserPendingEmailVerifications.query.filter_by(user_id=client_id).first().token
    request = test_client.get(
        f'/user/email-verification/token/{token}/')

    #2. Create staff/client user
    payload = users_to_delete_data['staff_client_user']
    response = test_client.post(
        '/user/staff/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')
    staff_client_id = response.json['user_info']['user_id']

    #verify newly created staff member's email
    token = UserPendingEmailVerifications.query.filter_by(user_id=staff_client_id).first().token

    request = test_client.get(
        f'/user/email-verification/token/{token}/')

    staff_client_user = test_client.post(
        '/user/client/',
        data=dumps(payload['user_info']),
        content_type='application/json')

    #3. Add staff members to client's clinical care team so we can make a request to add data on their behalf
    email = users_to_delete_data['client_user']['email']
    passw = users_to_delete_data['client_user']['password']
    user = (test_client.db.session.execute(
        select(User)
        .filter_by(email=email))
        .one_or_none())[0]

    client_auth_header = login(test_client, user, password=passw)

    clients_clinical_care_team = {
        'care_team' : [{
            'team_member_email': users_to_delete_data['staff_client_user']['user_info']['email']}]}

    response = test_client.post(
        f'/client/clinical-care-team/members/{client_id}/',
        data=dumps(clients_clinical_care_team),
        headers=client_auth_header,
        content_type='application/json')

    total_resources = LookupClinicalCareTeamResources.query.count()
    auths = []
    for num in range(1, total_resources + 2):
        #must be length + 2 because id 4 was removed from the middle, making the count 1 less than the
        #highest index number
        #skip when num is 4 since that is the removed medications resource
        if num != 4:
            auths.append({
                'team_member_user_id': staff_client_id,
                'resource_id': num
            })

    payload = {'clinical_care_team_authorization' : auths}
    response = test_client.post(
        f'/client/clinical-care-team/resource-authorization/{client_id}/',
        headers=client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    #4. Add info for client user, reported by staff/client
    email = users_to_delete_data['staff_client_user']['user_info']['email']
    passw = users_to_delete_data['staff_client_user']['user_info']['password']
    staff = (test_client.db.session.execute(
        select(User)
        .filter_by(email=email))
        .one_or_none())[0]

    staff_auth_header = login(test_client, staff, password=passw)
    payload = doctor_medical_imaging_data

    response = test_client.post(
        f'/doctor/images/{client_id}/',
        headers=staff_auth_header,
        data=payload)

    assert response.status_code == 201

    # 5. Delete staff/client
    deleting_staff_client = test_client.delete(
        f'/system/delete-user/{staff_client_id}/?delete_type=both',
        headers=test_client.staff_auth_header)

    assert deleting_staff_client.status_code == 204

    # Check no info for user_id is in staff tables
    tables = test_client.db.session.execute(text(
        """ SELECT distinct(table_name)
            FROM information_schema.columns
            WHERE table_name LIKE 'Staff%';
        """)).fetchall()

    for table in tables:
        if table.table_name == 'StaffRecentClients':
            exists = test_client.db.session.execute(text(""" SELECT EXISTS( SELECT * FROM "{}" WHERE staff_user_id={});""".format(table.table_name, staff_client_id)))
            result = exists.fetchall().pop()
            assert result[0] == False
        else:
            exists = test_client.db.session.execute(text(""" SELECT EXISTS( SELECT * FROM "{}" WHERE user_id={});""".format(table.table_name, staff_client_id)))
            result = exists.fetchall().pop()
            assert result[0] == False

    assert tables

    # Check info reported by staff user on client user is still in db
    med_imaging_record = MedicalImaging.query.filter_by(user_id=client_id).first()

    assert med_imaging_record
    assert med_imaging_record.user_id == client_id
    assert med_imaging_record.reporter_id == staff_client_id

    # Check modobioid, userid, name, email are in User table, no phone#
    staff_user = User.query.filter_by(user_id=staff_client_id).first()

    assert staff_user.phone_number == None
    assert staff_user.modobio_id
    assert staff_user.user_id
    assert staff_user.firstname
    assert staff_user.lastname

    # 5. Delete client
    deleting_client = test_client.delete(
        f'/system/delete-user/{client_id}/?delete_type=client',
        headers=test_client.staff_auth_header)

    assert deleting_client.status_code == 204

    # Check only modobioid and userid are in User table
    client_user = User.query.filter_by(user_id=client_id).first()

    assert client_user.firstname == None
    assert client_user.lastname == None
    assert client_user.email == None
    assert client_user.phone_number == None
    assert client_user.modobio_id
    assert client_user.user_id

    # Check UserRemovalRequests tables is populated correctly
    removal_request = UserRemovalRequests.query.all()

    assert removal_request[0].user_id == staff_client_id
    assert removal_request[0].requester_user_id == test_client.staff_id
    assert removal_request[1].user_id == client_id
    assert removal_request[1].requester_user_id == test_client.staff_id
