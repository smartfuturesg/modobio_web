import base64

from flask.json import dumps

from tests.functional.client_services.data import client_services_register_user_client, client_services_register_user_staff

def test_new_client_user(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for creating a new client with the client services API
    WHEN the '/client-services/user/new/' resource  is requested (POST)
    THEN a portalId and new login password are generated
    """
    # register the new client user
    response = test_client.post('/client-services/user/new/', 
                                headers=staff_auth_header,
                                data=dumps(client_services_register_user_client),  
                                content_type='application/json')
    password = response.json['password']
    portal_id = response.json['portal_id']

    assert response.status_code == 201
    assert password
    assert portal_id

    ####
    # Verify the portal_id and complete client registration
    ####
    response = test_client.put(f'/user/registration-portal/verify?portal_id={portal_id}', 
                                headers=staff_auth_header)

    
    assert response.status_code == 200

    ####
    # Log in to ensure client has made it into the database
    ####

    valid_credentials = base64.b64encode(
            f"{client_services_register_user_client['email']}:{password}".encode("utf-8")).decode("utf-8")
    
    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post('/client/token/',
                            headers=headers, 
                            content_type='application/json')
    
    new_remote_user_id = response.json['user_id']

    assert response.status_code == 201
    assert response.json['email'] == client_services_register_user_client['email']

    ####
    # Attenmpt to log in as a staff member, should fail
    ####
    response = test_client.post('/staff/token/',
                        headers=headers, 
                        content_type='application/json')
    assert response.status_code == 401

    ####
    # Bring up ClientInfo for user
    ####
    response = test_client.get(f'/client/{new_remote_user_id}/', 
                        headers=staff_auth_header,
                        content_type='application/json')

    assert response.status_code == 200




def test_new_staff_user(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for creating a new user through the client services API
    WHEN the '/client-services/user/new/' resource  is requested (POST)
    THEN a portalId and new login password are generated
    """
    # register the new client user
    response = test_client.post('/client-services/user/new/', 
                                headers=staff_auth_header,
                                data=dumps(client_services_register_user_staff),  
                                content_type='application/json')

    password = response.json['password']
    portal_id = response.json['portal_id']

    assert response.status_code == 201
    assert password
    assert portal_id

    ####
    # Verify the portal_id and complete client registration
    ####
    response = test_client.put(f'/user/registration-portal/verify?portal_id={portal_id}', 
                                headers=staff_auth_header)
    
    assert response.status_code == 200

    ####
    # Log in to ensure client has made it into the database
    ####

    valid_credentials = base64.b64encode(
            f"{client_services_register_user_staff['email']}:{password}".encode("utf-8")).decode("utf-8")
    
    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post('/staff/token/',
                            headers=headers, 
                            content_type='application/json')

    assert response.status_code == 201
    assert response.json['email'] == client_services_register_user_staff['email']


    ####
    # Attenmpt to log in as a client, should fail
    ####
    response = test_client.post('/client/token/',
                        headers=headers, 
                        content_type='application/json')
                        
    assert response.status_code == 401
