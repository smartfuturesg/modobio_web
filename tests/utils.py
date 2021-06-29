"""
Utility funcitons and objects for resducing redundancy when writing tests

"""

import base64


def create_authorization_header(test_client, init_database, email, password, user_type):
    """
    Create a staff or client authorization header using the context of the running test provided as 
    the first two arguments (test_client, init_database)
    """
    valid_credentials = base64.b64encode(
            f"{email}:{password}".encode("utf-8")).decode("utf-8")
    headers = {'Authorization': f'Basic {valid_credentials}'}
    token_request_response = test_client.post(f'/{user_type}/token/',
            headers=headers,
            content_type='application/json')
    token = token_request_response.json.get('token')
    auth_header = {'Authorization': f'Bearer {token}'}

    return auth_header