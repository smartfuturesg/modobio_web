from flask import current_app
from odyssey.api.user.models import User
from odyssey.api.client.models import ClientInfo


def test_get_client_search(test_client):
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

    client = (test_client.db.session
        .query(User, ClientInfo)
        .filter_by(user_id=test_client.client_id)
        .join(ClientInfo)
        .first())

    response = test_client.get(
        f'/client/search/?modobio_id={client.User.modobio_id}',
        headers=test_client.staff_auth_header)

    assert response.status_code == 200
    assert response.json['items'][0]['firstname'] == client.User.firstname
    assert response.json['items'][0]['lastname'] == client.User.lastname
    assert response.json['items'][0]['email'] == client.User.email
    assert response.json['items'][0]['modobio_id'] == client.User.modobio_id
    assert response.json['items'][0]['phone_number'] == str(client.User.phone_number)
    assert response.json['items'][0]['dob'] == str(client.ClientInfo.dob)

    # send get request for first name
    response = test_client.get(
        f'/client/search/?firstname={client.User.firstname}',
        headers=test_client.staff_auth_header)

    assert response.status_code == 200
    assert response.json['items'][0]['firstname'] == client.User.firstname
    assert response.json['items'][0]['lastname'] == client.User.lastname
