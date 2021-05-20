from flask.json import dumps
from odyssey.api.client.models import ClientRaceAndEthnicity
from .data import clients_race_and_ethnicities

def test_post_client_race_and_ethnicity(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for submitting a client race and ethnicity
    WHEN the '/client/race-and-ethnicity/<user_id>/' resource  is requested (POST)
    THEN check the response is successful
    """
    #test with invalid data
    response = test_client.post("/client/race-and-ethnicity/1/",
                                headers=client_auth_header, 
                                data=dumps(clients_race_and_ethnicities['invalid race_id']), 
                                content_type='application/json')

    #invalid race_id should result in a 400 error
    assert response.status_code == 400

    #test with valid data
    response = test_client.post("/client/race-and-ethnicity/1/",
                                headers=client_auth_header, 
                                data=dumps(clients_race_and_ethnicities['normal data']), 
                                content_type='application/json')

    assert response.status_code == 201

    #test with valid data but user already has race and ethnicity data submitted
    response = test_client.post("/client/race-and-ethnicity/1/",
                            headers=client_auth_header, 
                            data=dumps(clients_race_and_ethnicities['normal data']), 
                            content_type='application/json')

    #should result in 400 error with a message to use PUT method
    assert response.status_code == 400



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

    #invalid race_id should result in a 400 error
    assert response.status_code == 400

    #test with valid data
    response = test_client.put("/client/race-and-ethnicity/1/",
                                headers=client_auth_header, 
                                data=dumps(clients_race_and_ethnicities['normal data']), 
                                content_type='application/json')

    assert response.status_code == 201