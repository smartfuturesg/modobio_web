
from flask.json import dumps

from tests.functional.client.data import clients_assigned_drinks

def test_post_client_assigned_drink(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for assigning a drink to a client
    WHEN the '/client/drinks/<client id>' resource  is requested to be added (POST)
    THEN the response the mapping of the client's user id to the drink id
    """
    
    response = test_client.post("/client/drinks/1/",
                                headers=staff_auth_header, 
                                data=dumps(clients_assigned_drinks), 
                                content_type='application/json')

    assert response.status_code == 201
    assert response.json.get('drink_id') == clients_assigned_drinks['drink_id']

    #test request when drink id does not exist
    clients_assigned_drinks['drink_id'] = 999999999

    response = test_client.post("/client/drinks/1/",
                            headers=staff_auth_header, 
                            data=dumps(clients_assigned_drinks), 
                            content_type='application/json')

    assert response.status_code == 404

def test_get_client_assigned_drinks(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for getting the drinks assigned to a client
    WHEN the '/client/drinks/<client id>' resource is requested (GET)
    THEN the the list of drinks assigned to the client will be returned
    """

    response = test_client.get("/client/drinks/1/",
                                headers=staff_auth_header, 
                                content_type='application/json')

    assert response.status_code == 200

def test_delete_client_assigned_drink(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for deleting an assigned drink from a client
    WHEN the '/client/drinks/<client id>' resource  is requested to be removed (DELETE)
    THEN the response will be 200
    """

    response = test_client.delete("/client/drinks/1/",
                                data=dumps({ "drink_ids": [1] }),
                                headers=staff_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200