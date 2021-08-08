from flask import current_app

def test_get_client_search(test_client, care_team):
    # Uses care_team fixture because staff member needs authorization to search client info

    # Skip test if no url is set for ELASTICSEARCH_URL
    # Prevents other developers from having to set up ES if they don't need it,
    # This test will not pass if there's a url set but the service isn't running
    if not current_app.elasticsearch:
        return

    # Simple search request by modobio_id and firstname
    response = test_client.get(
        '/client/search/',
        headers=test_client.staff_auth_header)

    assert response.status_code == 200

    # Search by modobio ID
    response = test_client.get(
        f'/client/search/?modobio_id={test_client.client.modobio_id}',
        headers=test_client.staff_auth_header)

    assert response.status_code == 200
    assert response.json['items'][0]['firstname'] == test_client.client.firstname
    assert response.json['items'][0]['lastname'] == test_client.client.lastname
    assert response.json['items'][0]['email'] == test_client.client.email
    assert response.json['items'][0]['modobio_id'] == test_client.client.modobio_id
    assert response.json['items'][0]['phone_number'] == str(test_client.client.phone_number)

    # Search by first name
    response = test_client.get(
        f'/client/search/?firstname={test_client.client.firstname}',
        headers=test_client.staff_auth_header)

    assert response.status_code == 200
    assert response.json['items'][0]['firstname'] == test_client.client.firstname
    assert response.json['items'][0]['lastname'] == test_client.client.lastname
