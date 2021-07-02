import base64

from flask.json import dumps
from sqlalchemy import text
from odyssey.api.lookup.models import LookupEHRPages

from odyssey.api.user.models import User, UserLogin, UserRemovalRequests, UserPendingEmailVerifications
from odyssey.api.doctor.models import MedicalImaging
from tests.functional.user.data import users_to_delete_data 
from tests.functional.doctor.data import doctor_medical_imaging_data
from tests.utils import create_authorization_header

from odyssey import db

def test_account_delete_request(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for deleting a user
    WHEN the 'DELETE /user/{user_id}' resource  is requested 
    THEN check the response is valid
    """

    #Just need two users added to db, one client and one staff/client
    #1. Create self created client user
    payload = users_to_delete_data['client_user']
    client_user = test_client.post('/user/client/', 
            data=dumps(payload), 
            content_type='application/json')
    client_id = client_user.json['user_info']['user_id']

    #verify newly created client's email
    token = UserPendingEmailVerifications.query.filter_by(user_id=client_id).first().token
    request = test_client.get(f'/user/email-verification/token/{token}/')
    
    #2. Create staff/cient user
    payload = users_to_delete_data['staff_client_user']
    response = test_client.post('/user/staff/',
            headers=staff_auth_header, 
            data=dumps(payload),
            content_type='application/json')
    staff_client_id = response.json['user_info']['user_id']

    #verify newly created staff member's email
    token = UserPendingEmailVerifications.query.filter_by(user_id=staff_client_id).first().token
    request = test_client.get(f'/user/email-verification/token/{token}/')
    
    staff_client_user = test_client.post('/user/client/',
            data=dumps(payload['user_info']),
            content_type='application/json')
    


    #3. Add staff members to client's clinical care team so we can make a request to add data on their behalf
    
    client_auth_header = create_authorization_header(test_client, 
    init_database, 
    users_to_delete_data['client_user']['email'], 
    users_to_delete_data['client_user']['password'],
    'client')

    clients_clinical_care_team = {'care_team' : [{'team_member_email': users_to_delete_data['staff_client_user']['user_info']['email']}]}
    response = test_client.post(f"/client/clinical-care-team/members/{client_id}/",
                                data=dumps(clients_clinical_care_team),
                                headers=client_auth_header, 
                                content_type='application/json')

    total_resources = LookupEHRPages.query.count()
    auths = [{"team_member_user_id": staff_client_id,"resource_group_id": num} for num in range(1,total_resources+1) ]
    payload = {"ehr_page_authorizations" : auths}
    response = test_client.post(f"/client/clinical-care-team/ehr-page-authorization/{client_id}/",
                            headers=client_auth_header,
                            data=dumps(payload), 
                            content_type='application/json')
    
    #4. Add info for client user, reported by staff/client
    staff_user_auth_header = create_authorization_header(
            test_client, 
            init_database, 
            users_to_delete_data['staff_client_user']['user_info']['email'], 
            users_to_delete_data['staff_client_user']['user_info']['password'],
            'staff')

    payload = doctor_medical_imaging_data
    response = test_client.post(f'/doctor/images/{client_id}/',
            headers=staff_user_auth_header,
            data = payload)
            
    print(response.data)
    assert response.status_code == 201
    
    #5. Delete staff/client
    deleting_staff_client = test_client.delete(f'/user/{staff_client_id}/',
            headers=staff_user_auth_header)

    assert deleting_staff_client.status_code == 200
    assert deleting_staff_client.json['message'] == f"User with id {staff_client_id} has been removed"
    
    #Check no info for user_id is in staff tables
    tableList = db.session.execute(text("SELECT distinct(table_name) from information_schema.columns\
                WHERE table_name like 'Staff%';")).fetchall()
                
    for table in tableList:
        exists = db.session.execute(text("SELECT EXISTS(SELECT * from \"{}\" WHERE user_id={});".format(table.table_name, staff_client_id)))
        result = exists.fetchall().pop()
        assert result[0] == False
    assert tableList

    #   -Check info reported by staff user on client user is still in db
    med_imaging_record = MedicalImaging.query.filter_by(user_id=client_id).first()
    assert med_imaging_record
    assert med_imaging_record.user_id == client_id
    assert med_imaging_record.reporter_id == staff_client_id

    #   -Check modobioid, userid, name, email are in User table, no phone#
    staff_user = User.query.filter_by(user_id=staff_client_id).first()
    assert staff_user.phone_number == None
    assert staff_user.modobio_id
    assert staff_user.user_id
    assert staff_user.firstname
    assert staff_user.lastname
    assert staff_user.email

    #5. Delete client
    deleting_client = test_client.delete(f'/user/{client_id}/',
                headers=staff_auth_header)
    assert deleting_client.status_code == 200

    #   -Check only modobioid and userid are in User table
    client_user = User.query.filter_by(user_id=client_id).first()
    assert client_user.firstname == None
    assert client_user.lastname == None
    assert client_user.email == None
    assert client_user.phone_number == None
    assert client_user.modobio_id
    assert client_user.user_id

    #   -Check UserRemovalRequests tables is populated correctly
    removal_request = UserRemovalRequests.query.all()
    assert removal_request[0].user_id == staff_client_id
    assert removal_request[0].requester_user_id == staff_client_id
    assert removal_request[1].user_id == client_id
    #requester is the staff member created in conftest
    assert removal_request[1].requester_user_id == 2


    
