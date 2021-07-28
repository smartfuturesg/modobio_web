from flask import current_app
from odyssey.api.user.models import User
from odyssey.api.client.models import ClientClinicalCareTeam, ClientInfo

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

    client_info = (test_client.db.session
        .query(ClientInfo)
        .filter_by(user_id=test_client.client_id)
        .one_or_none())

    # Add staff to client's care team so the client can be searched
    ccct = ClientClinicalCareTeam(
        team_member_user_id=test_client.staff_id,
        user_id=test_client.client_id)
    test_client.db.session.add()
    test_client.db.session.commit()

    # Search by modobio ID
    response = test_client.get(
        f'/client/search/?modobio_id={test_client.client.modobio_id}',
        headers=test_client.staff_auth_header)

    assert response.status_code == 200
    assert response.json['items'][0]['firstname'] == test_client.client.firstname
    assert response.json['items'][0]['lastname'] == test_client.client.lastname
    assert response.json['items'][0]['email'] == test_client.client_email
    assert response.json['items'][0]['modobio_id'] == test_client.client.modobio_id
    assert response.json['items'][0]['phone_number'] == str(test_client.client.phone_number)
    assert response.json['items'][0]['dob'] == str(client_info.dob)

    # Search by first name
    response = test_client.get(
        f'/client/search/?firstname={test_client.client.firstname}',
        headers=test_client.staff_auth_header)

    assert response.status_code == 200
    assert response.json['items'][0]['firstname'] == test_client.client.firstname
    assert response.json['items'][0]['lastname'] == test_client.client.lastname
