
import pytest
from sqlalchemy import select
from odyssey.api.user.models import User

from odyssey.integrations.twilio import Twilio
from odyssey.tasks.periodic import deploy_appointment_transcript_store_tasks
from odyssey.tasks.tasks import store_telehealth_transcript


def test_twilio_wrapper(test_client, booking_twilio):
    """
    Test the twilio wrapper
    - using a new telehealth booking
    - send a few messages by each participant
    - close conversation
    - bring up chat transcript
    
    """
    twilio = Twilio()

    booking = booking_twilio

    conversation_sid = booking.chat_room.conversation_sid

    # add test image file to twilio 
    media_sid = twilio.upload_media(media_path='tests/functional/telehealth/test_img_weirdmole.jpg')

    # add a few messages
    #staff
    twilio.send_message(
        user_id = booking.staff_user_id, 
        conversation_sid = conversation_sid,
        message_body = "hello, how are you?")

    #client
    twilio.send_message(
        user_id = booking.client_user_id, 
        conversation_sid = conversation_sid,
        message_body = "hi. Great, and you?")
    #staff
    twilio.send_message(
        user_id = booking.staff_user_id, 
        conversation_sid = conversation_sid,
        message_body = "fine, how are you?")
    #client
    twilio.send_message(
        user_id = booking.client_user_id, 
        conversation_sid = conversation_sid,
        message_body = "... I'm okay")

    # add media file to conversation transcript
    twilio.send_message(
        user_id = booking.client_user_id, 
        conversation_sid = conversation_sid,
        media_sid = media_sid)

    # close the chat to further messages
    twilio.close_telehealth_chatroom(booking.idx)
    
    # bring up the chat transcript
    transcript = twilio.get_booking_transcript(booking.idx)

    # bring up media
    for message in transcript:
        if message['media']:
            for media in message['media']:
                media_url = twilio.get_media(media['sid'])

    assert True

def test_conversation_cache(test_client, booking_twilio):
    """
    Test the conversation cache task which takes a booking_id and stores the conversation on mongo_db. All media is stored in an s3 bucket.
    
    - using a new telehealth booking
    - send a few messages by each participant
    - cache conversation

    Checks
    - ensure the booking transcript is sucessfully pulled out of the twilio platform. 
    - check the path to the stored media  
    """
    twilio = Twilio()
    booking = booking_twilio
    conversation_sid = booking.chat_room.conversation_sid

    # add test image file to twilio 
    media_sid = twilio.upload_media(media_path='tests/functional/telehealth/test_img_weirdmole.jpg')

    # add a few messages
    #staff
    twilio.send_message(
        user_id = booking.staff_user_id, 
        conversation_sid = conversation_sid,
        message_body = "testingtesting")

    
    # add media file to conversation transcript
    twilio.send_message(
        user_id = booking.client_user_id, 
        conversation_sid = conversation_sid,
        media_sid = media_sid)

    stored_transcript = store_telehealth_transcript(booking.idx)

    fname = f'id{test_client.client_id:05d}/telehealth/{booking.idx}/transcript/images/0.jpeg'

    assert len(stored_transcript['transcript']) == 2
    assert stored_transcript['transcript'][1]['media'][0]['s3_path'] == fname
    
def test_conversation_cache_scheduler(test_client, booking_twilio):
    """
    Test the conversation cache task which takes a booking_id and stores the conversation on mongo_db. All media is stored in an s3 bucket.
    
    - using a new telehealth booking
    - send a few messages by each participant
    - cache conversation

    Checks
    - ensure the booking transcript is sucessfully pulled out of the twilio platform. 
    - check the path to the stored media  
    """
    twilio = Twilio()
    booking = booking_twilio
    conversation_sid = booking.chat_room.conversation_sid

    # add test image file to twilio 
    media_sid = twilio.upload_media(media_path='tests/functional/telehealth/test_img_weirdmole.jpg')

    # add a few messages
    #staff
    twilio.send_message(
        user_id = booking.staff_user_id, 
        conversation_sid = conversation_sid,
        message_body = "testingtesting")

    
    # add media file to conversation transcript
    twilio.send_message(
        user_id = booking.client_user_id, 
        conversation_sid = conversation_sid,
        media_sid = media_sid)


    # test the scheduler 
    bookings = deploy_appointment_transcript_store_tasks(booking.target_date)

def test_telehealth_transcript_get(test_client, booking_twilio):
    """
    Testing the API for retrieving telehealth transcripts stored on the modobio end. Only bookings which have 
    passed the post-booking review period will have transcripts stored. 

    Test:
    -create new booking
    -add messages, one of those messages contains media
    -run the teask to store the transcipt (tested above)
    -query GET /telehealth/bookings/transcript/{booking.idx}/
    """
    twilio = Twilio()
    booking = booking_twilio
    conversation_sid = booking.chat_room.conversation_sid

    # add test image file to twilio 
    media_sid = twilio.upload_media(media_path='tests/functional/telehealth/test_img_weirdmole.jpg')

    # add a few messages
    #staff
    twilio.send_message(
        user_id = booking.staff_user_id, 
        conversation_sid = conversation_sid,
        message_body = "testingtesting")

    
    # add media file to conversation transcript
    twilio.send_message(
        user_id = booking.client_user_id, 
        conversation_sid = conversation_sid,
        media_sid = media_sid)

    stored_transcript = store_telehealth_transcript(booking.idx)

    response = test_client.get(
        f'/telehealth/bookings/transcript/{booking.idx}/',
        headers=test_client.client_auth_header
    )
    
    assert response.status_code == 200
    assert len(response.json['transcript'][1]['media']) == 1
    assert response.json['transcript'][1]['media'][0]['content_type'] == 'image/jpeg'

def test_telehealth_bookings_get(test_client, booking_twilio):
    """
    Testing the API for retrieving telehealth bookings..again. This time the focus is on retrieving the details of the
    stored transcripts along with the rest of the booking details.  

    Test:
    -create new booking
    -add messages, one of those messages contains media
    -run the teask to store the transcipt (tested above)
    -query GET /telehealth/bookings/{booking.idx}/

    The response is expected to include a link to retrieve the stored transcript
    """

    twilio = Twilio()
    booking = booking_twilio
    conversation_sid = booking.chat_room.conversation_sid

    # add test image file to twilio 
    media_sid = twilio.upload_media(media_path='tests/functional/telehealth/test_img_weirdmole.jpg')

    # add a few messages
    #staff
    twilio.send_message(
        user_id = booking.staff_user_id, 
        conversation_sid = conversation_sid,
        message_body = "testingtesting")

    
    # add media file to conversation transcript
    twilio.send_message(
        user_id = booking.client_user_id, 
        conversation_sid = conversation_sid,
        media_sid = media_sid)

    stored_transcript = store_telehealth_transcript(booking.idx)

    response = test_client.get(
        f'/telehealth/bookings/?booking_id={booking.idx}',
        headers=test_client.client_auth_header
    )

    assert response.status_code == 200
    assert response.json['bookings'][0]['chat_room']['transcript_url']
    
