
import base64

from flask.json import dumps
from flask_accepts.decorators.decorators import responds

from odyssey.api.lookup.models import LookupClinicalCareTeamResources

from tests.functional.client.data import clients_clinical_care_team
from tests.functional.user.data import users_new_user_client_data, users_staff_member_data

def test_adding_clinical_care_team(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for adding members to a client's care team
    WHEN the '/client/clinical-care-team/<client id>' resource  is requested to be added (POST)
    THEN the response will be the emails of the client's care team
    """
    
    clients_clinical_care_team['care_team'].append(
        {
            'team_member_email': users_new_user_client_data['user_info']['email']
        })
    
    response = test_client.post(f"/client/clinical-care-team/members/{1}/",
                                headers=client_auth_header, 
                                data=dumps(clients_clinical_care_team), 
                                content_type='application/json')

    assert response.status_code == 201
    assert response.json.get("total_items") == 3
    assert response.json.get("care_team")

    #check that the person added to the client's care team above sees the client
    #when viewing the list of clients whose care team they belong to
    response = test_client.get("/client/clinical-care-team/member-of/3/",
                                headers=staff_auth_header,
                                content_type='application/json')
    
    assert response.status_code == 200
    assert response.json['member_of_care_teams'][0]['client_user_id'] == 1

    ###
    # Attempt to add more than 20 clinical care team members
    ###

    clients_clinical_care_team['care_team'].extend([
        {
            'team_member_email': 'email1@modo.com'
        },
        {
            'team_member_email': 'email2@modo.com'
        },
        {
            'team_member_email': 'email42@modo.com'
        },
        {
            'team_member_email': 'email3@modo.com'
        },
        {
            'team_member_email': 'email42@modo.com'
        },
        {
            'team_member_email': 'email6@modo.com'
        },
        {
            'team_member_email': 'email7@modo.com'
        },
        {
            'team_member_email': 'email8@modo.com'
        },
        {
            'team_member_email': 'email9@modo.com'
        },
        {
            'team_member_email': 'email10@modo.com'
        },
        {
            'team_member_email': 'email11@modo.com'
        },
        {
            'team_member_email': 'email12@modo.com'
        },
        {
            'team_member_email': 'email13@modo.com'
        },
        {
            'team_member_email': 'email14@modo.com'
        },
        {
            'team_member_email': 'email15@modo.com'
        },
        {
            'team_member_email': 'email16@modo.com'
        },
        {
            'team_member_email': 'email17@modo.com'
        },
        {
            'team_member_email': 'email18@modo.com'
        },
        {
            'team_member_email': 'email19@modo.com'
        }
    ]
    )


    response = test_client.post(f"/client/clinical-care-team/members/{1}/",
                            headers=client_auth_header, 
                            data=dumps(clients_clinical_care_team), 
                            content_type='application/json')

    assert response.status_code == 400

def test_delete_clinical_care_team(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for adding members to a client's care team
    WHEN the '/client/clinical-care-team/<client id>' resource deletion is request is made (DELETE)
    THEN the response will be 200
    """

    # remove one email from the list of clinical care team members 
    clients_clinical_care_team['care_team'].remove({
        'team_member_email': users_new_user_client_data['user_info']['email']
        })

    response = test_client.delete(f"/client/clinical-care-team/members/{1}/",
                                data=dumps(clients_clinical_care_team),
                                headers=client_auth_header, 
                                content_type='application/json')

    assert response.status_code == 200

def test_get_clinical_care_team(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for adding members to a client's care team
    WHEN the '/client/clinical-care-team/<client id>' resource  is requested (GET)
    THEN the response will be the emails of the client's care team
    """
    global team_member_user_id

    
    response = test_client.get(f"/client/clinical-care-team/members/{1}/",
                                headers=client_auth_header, 
                                content_type='application/json')

    team_member = response.json.get("care_team")[0]
    
    assert response.status_code == 200
    assert response.json.get("total_items") == 1
    assert team_member.get('team_member_user_id') 
    assert team_member.get('team_member_email') 
    assert team_member.get('firstname') 
    assert team_member.get('lastname') 

    team_member_user_id = team_member.get('team_member_user_id') 

    clients_clinical_care_team['care_team'].remove(
        {
            'team_member_email': 'email1@modo.com'
        })
    clients_clinical_care_team['care_team'].remove(
        {
            'team_member_email': 'email2@modo.com'}
        )
    clients_clinical_care_team['care_team'].remove(
        {
            'team_member_email': 'email3@modo.com'}
        )          
    clients_clinical_care_team['care_team'].extend([{
        'team_member_email': 'staff_member@modobio.com'
        }])    
    response = test_client.post(f"/client/clinical-care-team/members/{1}/",
                                headers=client_auth_header, 
                                data=dumps(clients_clinical_care_team), 
                                content_type='application/json')
    assert response.status_code == 201    

def test_authorize_clinical_care_team(test_client, init_database, client_auth_header,staff_auth_header):
    """
    GIVEN a api end point for authorizing the use of resources for members of a client's care team
    WHEN the '/client/clinical-care-team/resource-authorization/<user_id>' resource  is requested (POST, GET)
    THEN the client's clinical care team will have authorizations stored in the databse which are retrievable
    by the same endpoint
    """

    total_resources = LookupClinicalCareTeamResources.query.count()

    auths = [{"team_member_user_id": team_member_user_id,"resource_id": num} for num in range(1,total_resources+1) ]
    payload = {"clinical_care_team_authorization" : auths}
    
    #####
    # Authorize another client to access all clinical care team resources
    #####
    response = test_client.post(f"/client/clinical-care-team/resource-authorization/{1}/",
                            headers=client_auth_header,
                            data=dumps(payload), 
                            content_type='application/json')
    assert response.status_code == 201

    #####
    # Try to authorize a resource that doesnt exist
    ####
    payload = {"clinical_care_team_authorization" : [{"team_member_user_id": team_member_user_id,"resource_id": 999999}]}

    response = test_client.post(f"/client/clinical-care-team/resource-authorization/{1}/",
                        headers=client_auth_header,
                        data=dumps(payload), 
                        content_type='application/json')

    assert response.status_code == 400

    #####
    # Try to authorize a resource for a client not part of the care team that doesnt exist
    ####
    payload = {"clinical_care_team_authorization" : [{"team_member_user_id": 99,"resource_id": 1}]}

    response = test_client.post(f"/client/clinical-care-team/resource-authorization/{1}/",
                        headers=client_auth_header,
                        data=dumps(payload), 
                        content_type='application/json')
    
    assert response.status_code == 400

    #####
    # Get authorizations
    #####
    response = test_client.get(f"/client/clinical-care-team/resource-authorization/{1}/",
                            headers=client_auth_header,
                            content_type='application/json')

    assert response.status_code == 200
    assert response.json['clinical_care_team_authorization'][0]['status'] == 'accepted'


    # Create payload for team_member_user_id 2 (a staff member)
    payload = {"clinical_care_team_authorization" : [{"team_member_user_id": 2,"resource_id": 1}]}
    
    #####
    # as a staff member, post for data access.
    #####
    response = test_client.post(f"/client/clinical-care-team/resource-authorization/{1}/",
                            headers=staff_auth_header,
                            data=dumps(payload), 
                            content_type='application/json')
    
    assert response.status_code == 201

    response = test_client.get(f"/client/clinical-care-team/resource-authorization/{1}/",
                            headers=client_auth_header,
                            content_type='application/json')

    assert response.status_code == 200
    assert response.json['clinical_care_team_authorization'][0]['status'] == 'accepted'
    
    # The staff member requested data access of resource id = 1 from user_id 1
    # The status was automatically set to 'pending' 
    for idx,info in enumerate(response.json['clinical_care_team_authorization']):
        if info['team_member_email'] == 'staff_member@modobio.com':
            assert response.json['clinical_care_team_authorization'][idx]['status'] == 'pending'

    # Now, note the header has switched to the client_auth_header indicating we are now the client of interest
    # We will now approve of this data access request.
    response = test_client.put(f"/client/clinical-care-team/resource-authorization/{1}/",
                            headers=client_auth_header,
                            data=dumps(payload), 
                            content_type='application/json')
    
    response = test_client.get(f"/client/clinical-care-team/resource-authorization/{1}/",
                            headers=client_auth_header,
                            content_type='application/json')

    assert response.status_code == 200                            
    for idx,info in enumerate(response.json['clinical_care_team_authorization']):
        if info['team_member_email'] == 'staff_member@modobio.com':
            assert response.json['clinical_care_team_authorization'][idx]['status'] == 'accepted'    


def test_clinical_care_team_access(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for authorizing the use of resources for members of a client's care team
    WHEN any authorized resource is requested (POST, GET)
    THEN the client's clinical care team will have authorizations stored in the databse which are retrievable
    by the same endpoint

    The intention of this test is to run through the authorization routine once. Rather than testing each endpoint
    that could be used by a care team member. 
    """
    valid_credentials = base64.b64encode(
        f"{users_new_user_client_data['user_info']['email']}:{'password'}".encode(
            "utf-8")).decode("utf-8")
    
    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post('/client/token/',
                            headers=headers, 
                            content_type='application/json')
    token = response.json.get('token')
    team_member_user_id = response.json.get('user_id')

    auth_header = {'Authorization': f'Bearer {token}'}
    
    #####
    # Try to grab the blood tests and social history this client has submitted
    #####
    response = test_client.get(f"/doctor/bloodtest/all/{1}/",
                                headers=auth_header,
                                content_type='application/json')

    assert response.status_code == 204 # no content submitted yet but, sucessful request
    
    response = test_client.get(f"/doctor/medicalinfo/social/{1}/",
                                headers=auth_header,
                                content_type='application/json')

    assert response.status_code == 200
    
    

