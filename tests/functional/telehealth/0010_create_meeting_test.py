import time 

from flask.json import dumps

from odyssey.api.user.models import User
from odyssey.api.telehealth.models import TelehealthMeetingRooms


def test_post_create_new_meeting(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for provisioning a meeting room
    WHEN the '/telehealth/meeting-room/new/<user_id>' resource  is requested (POST)
    THEN meeting room details are returned
    """
    global meeting_room_id
    
    # find a client user 
    client_user = User.query.filter_by(is_client=True).first()
    # send get request for client info on clientid = 1 
    response = test_client.post(f'/telehealth/meeting-room/new/{client_user.user_id}/',
                                headers=staff_auth_header, 
                                content_type='application/json')

    
    meeting_room_id = response.json.get('room_id',None)
    # bring up the meeting room
    meeting_room = TelehealthMeetingRooms.query.filter_by(room_id = meeting_room_id).one_or_none()
    
    assert response.status_code == 201
    assert len([*response.json]) == 4
    assert meeting_room.staff_access_token == response.json['access_token']

def test_access_meeting_as_client(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for provisioning a meeting room access token as a client
    WHEN the '/telehealth/meeting-room/access-token/<room_id>' resource  is requested (POST)
    THEN a meeting room access token is returned
    """

    response = test_client.post(f'/telehealth/meeting-room/access-token/{meeting_room_id}/',
                            headers=client_auth_header, 
                            content_type='application/json')

    # bring up the meeting room
    meeting_room = TelehealthMeetingRooms.query.filter_by(room_id = meeting_room_id).one_or_none()

    assert response.status_code == 201
    assert len([*response.json]) == 4
    assert meeting_room.room_name == response.json['room_name']
    assert meeting_room.client_access_token == response.json['access_token']


def test_meeting_room_status(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for checking meeting room status
    WHEN the '/telehealth/meeting-room/status/<room_id>' resource  is requested (GET)
    THEN a meeting room status token is returned
    """

    response = test_client.get(f'/telehealth/meeting-room/status/{meeting_room_id}/',
                            headers=client_auth_header, 
                            content_type='application/json')

    assert response.status_code == 200