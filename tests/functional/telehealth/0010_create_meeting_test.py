import pytest
from sqlalchemy import select

from odyssey.api.user.models import User
from odyssey.api.telehealth.models import TelehealthChatRooms,TelehealthMeetingRooms

@pytest.mark.skip('This endpoint should no longer be used.')
def test_post_create_new_meeting(test_client):
    global meeting_room_id
    global client_user_id
    global staff_user_id
    # find a client user
    client_user = User.query.filter_by(is_client=True).first()
    client_user_id = client_user.user_id
    # send get request for client info on clientid = 1
    response = test_client.post(
        f'/telehealth/meeting-room/new/{client_user.user_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    meeting_room_id = response.json.get('room_id', None)

    # bring up the meeting room and chat room so we are certain they are populated in the DB
    meeting_room = TelehealthMeetingRooms.query.filter_by(room_id = meeting_room_id).one_or_none()
    chat_room = test_client.db.session.execute(select(
        TelehealthChatRooms
        ).where(
            TelehealthChatRooms.client_user_id == client_user.user_id)
        ).one_or_none()

    staff_user_id = chat_room[0].staff_user_id

    assert response.status_code == 201
    assert len([*response.json]) == 5
    assert meeting_room.staff_access_token == response.json['access_token']
    assert response.json['conversation_sid'] == chat_room[0].conversation_sid

@pytest.mark.skip('This endpoint should no longer be used.')
def test_access_meeting_as_client(test_client):
    response = test_client.post(
        f'/telehealth/meeting-room/access-token/{meeting_room_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    # bring up the meeting room
    meeting_room = TelehealthMeetingRooms.query.filter_by(room_id = meeting_room_id).one_or_none()
    chat_room = test_client.db.session.execute(select(
        TelehealthChatRooms
        ).where(
            TelehealthChatRooms.client_user_id == meeting_room.client_user_id)
        ).one_or_none()

    assert response.status_code == 201
    assert len([*response.json]) == 5
    assert meeting_room.room_name == response.json['room_name']
    assert meeting_room.client_access_token == response.json['access_token']
    assert response.json['conversation_sid'] == chat_room[0].conversation_sid

@pytest.mark.skip('This endpoint should no longer be used.')
def test_meeting_room_status(test_client):
    response = test_client.get(
        f'/telehealth/meeting-room/status/{meeting_room_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200

@pytest.mark.skip('This endpoint should no longer be used.')
def test_getting_access_to_chat_room(test_client):
    # generate a chat room access token as a staff member
    response = test_client.post(
        f'/telehealth/chat-room/access-token?client_user_id={client_user_id}&staff_user_id={staff_user_id}',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    chat_room = test_client.db.session.execute(select(
        TelehealthChatRooms
        ).where(
            TelehealthChatRooms.client_user_id == client_user_id),
            TelehealthChatRooms.staff_user_id == staff_user_id
        ).one_or_none()

    assert response.status_code == 201
    assert response.json['access_token']
    assert response.json['conversation_sid'] == chat_room[0].conversation_sid

    # generate a chat room access token as a client member
    response = test_client.post(
        f'/telehealth/chat-room/access-token?client_user_id={client_user_id}&staff_user_id={staff_user_id}',
        headers=test_client.client_auth_header,
        content_type='application/json')

    chat_room = test_client.db.session.execute(select(
        TelehealthChatRooms
        ).where(
            TelehealthChatRooms.client_user_id == client_user_id),
            TelehealthChatRooms.staff_user_id == staff_user_id
        ).one_or_none()

    assert response.status_code == 201
    assert response.json['access_token']
    assert response.json['conversation_sid'] == chat_room[0].conversation_sid
