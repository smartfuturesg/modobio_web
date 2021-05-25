from flask.json import dumps
from odyssey.api.client.models import ClientRaceAndEthnicity
from .data import clients_race_and_ethnicities

def test_get_client_race_and_ethnicity(test_client, init_database, client_auth_header):
    """
    GIVEN an api end point for getting the race and ethnicity information of a client
    WHEN the '/client/race-and-ethnicity/<user_id>/' resource is requested (GET)
    THEN the race and ethnicity data of the client is returned
    """

    response = test_client.get("/client/race-and-ethnicity/1/",
                                headers=client_auth_header, 
                                content_type='application/json')

    assert response.status_code == 200

def test_put_client_race_and_ethnicity(test_client, init_database, client_auth_header):
    """
    GIVEN an api end point for updating a client's race and ethnicity information
    WHEN the '/client/race-and-ethnicity/<user_id>/' resource  is requested (PUT)
    THEN check the response is successful
    """
    
    #test with invalid data
    response = test_client.put("/client/race-and-ethnicity/1/",
                                headers=client_auth_header, 
                                data=dumps(clients_race_and_ethnicities['invalid race_id']), 
                                content_type='application/json')
    assert response.status_code == 400

    #test with valid data
    response = test_client.put("/client/race-and-ethnicity/1/",
                                headers=client_auth_header, 
                                data=dumps(clients_race_and_ethnicities['normal data']), 
                                content_type='application/json')
    assert response.status_code == 201

    #test with valid data(empty array for 1 parent, assigns id 1 (unknown) for that parent)
    response = test_client.put("/client/race-and-ethnicity/1/",
                            headers=client_auth_header, 
                            data=dumps(clients_race_and_ethnicities['unknown']), 
                            content_type='application/json')
    assert response.status_code == 201

    #test with invalid data (id 1 in a list with other ids)
    response = test_client.put("/client/race-and-ethnicity/1/",
                        headers=client_auth_header, 
                        data=dumps(clients_race_and_ethnicities['invalid combination']), 
                        content_type='application/json')
    assert response.status_code == 400

    #test with list containing all valid ids (except 1)
    response = test_client.put("/client/race-and-ethnicity/1/",
                            headers=client_auth_header, 
                            data=dumps(clients_race_and_ethnicities['all ids']), 
                            content_type='application/json')
    assert response.status_code == 201

    #test with list containing duplicate ids (should still work, duplicates will be ignored)
    response = test_client.put("/client/race-and-ethnicity/1/",
                            headers=client_auth_header, 
                            data=dumps(clients_race_and_ethnicities['duplicates']), 
                            content_type='application/json')
    assert response.status_code == 201

    #test with list containing an invalid data type
    response = test_client.put("/client/race-and-ethnicity/1/",
                            headers=client_auth_header, 
                            data=dumps(clients_race_and_ethnicities['non-numeric']), 
                            content_type='application/json')
    assert response.status_code == 400