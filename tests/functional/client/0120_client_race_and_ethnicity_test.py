from flask.json import dumps
from odyssey.api.client.models import ClientRaceAndEthnicity
from .data import clients_race_and_ethnicities

def test_get_client_race_and_ethnicity(test_client):
    response = test_client.get(
        f"/client/race-and-ethnicity/{test_client.client_id}/",
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200

def test_put_client_race_and_ethnicity(test_client):
    #test with invalid data
    response = test_client.put(
        f"/client/race-and-ethnicity/{test_client.client_id}/",
        headers=test_client.client_auth_header,
        data=dumps(clients_race_and_ethnicities['invalid race_id']),
        content_type='application/json')

    assert response.status_code == 400

    #test with valid data
    response = test_client.put(
        f"/client/race-and-ethnicity/{test_client.client_id}/",
        headers=test_client.client_auth_header,
        data=dumps(clients_race_and_ethnicities['normal data']),
        content_type='application/json')

    assert response.status_code == 201

    #test with valid data(empty array for 1 parent, assigns id 1 (unknown) for that parent)
    response = test_client.put(
        f"/client/race-and-ethnicity/{test_client.client_id}/",
        headers=test_client.client_auth_header,
        data=dumps(clients_race_and_ethnicities['unknown']),
        content_type='application/json')

    assert response.status_code == 201

    #test with invalid data (id 1 in a list with other ids)
    response = test_client.put(
        f"/client/race-and-ethnicity/{test_client.client_id}/",
        headers=test_client.client_auth_header,
        data=dumps(clients_race_and_ethnicities['invalid combination']),
        content_type='application/json')

    assert response.status_code == 400

    #test with list containing all valid ids (except 1)
    response = test_client.put(
        f"/client/race-and-ethnicity/{test_client.client_id}/",
        headers=test_client.client_auth_header,
        data=dumps(clients_race_and_ethnicities['all ids']),
        content_type='application/json')

    assert response.status_code == 201

    #test with list containing duplicate ids (should still work, duplicates will be ignored)
    response = test_client.put(
        f"/client/race-and-ethnicity/{test_client.client_id}/",
        headers=test_client.client_auth_header,
        data=dumps(clients_race_and_ethnicities['duplicates']),
        content_type='application/json')

    assert response.status_code == 201

    #test with list containing an invalid data type
    response = test_client.put(
        f"/client/race-and-ethnicity/{test_client.client_id}/",
        headers=test_client.client_auth_header,
        data=dumps(clients_race_and_ethnicities['non-numeric']),
        content_type='application/json')

    assert response.status_code == 400
