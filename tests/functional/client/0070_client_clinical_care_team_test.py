
from flask.json import dumps

from tests.functional.client.data import clients_clinical_care_team
from tests.functional.user.data import users_new_user_client_data
def test_adding_clinical_care_team(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for adding members to a client's care team
    WHEN the '/client/clinical-care-team/<client id>' resource  is requested to be added (POST)
    THEN the response will be the emails of the client's care team
    """
    
    clients_clinical_care_team['care_team'].append(
        {
            'team_member_email': users_new_user_client_data['user_info']['email']
        })
    
    response = test_client.post(f"/client/clinical-care-team/{1}/",
                                headers=client_auth_header, 
                                data=dumps(clients_clinical_care_team), 
                                content_type='application/json')

    
    assert response.status_code == 201
    assert response.json.get("total_items") == 3
    assert response.json.get("care_team")


    ###
    # Attempt to add more than 6 clinical care team members
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
        }
    ]
    )


    response = test_client.post(f"/client/clinical-care-team/{1}/",
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

    response = test_client.delete(f"/client/clinical-care-team/{1}/",
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

    
    response = test_client.get(f"/client/clinical-care-team/{1}/",
                                headers=client_auth_header, 
                                content_type='application/json')

    team_member = response.json.get("care_team")[0]
    
    assert response.status_code == 200
    assert response.json.get("total_items") == 1
    assert team_member.get('team_member_user_id') 
    assert team_member.get('team_member_email') 
    assert team_member.get('firstname') 
    assert team_member.get('lastname') 