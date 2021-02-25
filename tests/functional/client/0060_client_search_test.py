from flask import current_app
from odyssey import db, defaults
from odyssey.api.user.models import User
from odyssey.api.client.models import ClientInfo


def test_get_client_search(test_client, init_database, staff_auth_header):
    """
    GIVEN an api end point for retrieving client info
    WHEN the '/client/search?<parameters>' resource  is requested (GET)
    THEN check the response is valid
    """
    # Skip test if no url is set for ELASTICSEARCH_URL
    # Prevents other developers from having to set up ES if they don't need it,
    # This test will not pass if there's a url set but the service isn't running
    if not current_app.elasticsearch:
        return
    
    # Simple search request by modobio_id and firstname
    response = test_client.get('/client/search/', headers=staff_auth_header)
    assert response.status_code == 200

    client = db.session.query(User,ClientInfo).filter_by(is_client=True, deleted=False).join(ClientInfo).first()
    
    queryStr = f'/client/search/?modobio_id={client.User.modobio_id}'

    response = test_client.get(queryStr, headers=staff_auth_header)
    
    assert response.status_code == 200
    assert response.json['items'][0]['firstname'] == client.User.firstname
    assert response.json['items'][0]['lastname'] == client.User.lastname
    assert response.json['items'][0]['email'] == client.User.email
    assert response.json['items'][0]['modobio_id'] == client.User.modobio_id
    assert response.json['items'][0]['phone_number'] == client.User.phone_number
    assert response.json['items'][0]['dob'] == str(client.ClientInfo.dob)

    # send get request for first name
    response = test_client.get(f'/client/search/?firstname={client.User.firstname}', headers=staff_auth_header)
    assert response.status_code == 200
    assert response.json['items'][0]['firstname'] == client.User.firstname
    assert response.json['items'][0]['lastname'] == client.User.lastname
