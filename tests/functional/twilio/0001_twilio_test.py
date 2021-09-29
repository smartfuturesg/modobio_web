
import pytest
from sqlalchemy import select
from odyssey.api.user.models import User

from odyssey.integrations.twilio import Twilio
from odyssey.tasks.periodic import deploy_appointment_transcript_store_tasks
from odyssey.tasks.tasks import store_telehealth_transcript


IMG_SID='MEcfe48b95ffd08e4823728544753af3d8'

@pytest.mark.skip
def test_twilio_wrapper(test_client, telehealth_booking):
    """
    Test the twilio wrapper
    - using a new telehealth booking
    - send a few messages by each participant
    - close conversation
    - bring up chat transcript
    
    """

    booking = telehealth_booking

    twilio = Twilio()

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


def test_conversation_cache(test_client, telehealth_booking):
    """
    Test the conversation cache task which takes a booking_id and stores the conversation on mongo_db. All media is stored in an s3 bucket.
    
    - using a new telehealth booking
    - send a few messages by each participant
    - cache conversation

    Checks
    - ensure the booking transcript is sucessfully pulled out of the twilio platform. 
    - check the path to the stored media  
    """
    booking = telehealth_booking

    twilio = Twilio()

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
    
    assert len(stored_transcript['transcript']) == 2
    assert stored_transcript['transcript'][1]['media'][0]['s3_path'] == f"id00022/telehealth/{booking.idx}/transcript/images/0.jpeg"
    

@pytest.mark.skip
def test_conversation_cache_scheduler(test_client, telehealth_booking):
    """
    Test the conversation cache task which takes a booking_id and stores the conversation on mongo_db. All media is stored in an s3 bucket.
    
    - using a new telehealth booking
    - send a few messages by each participant
    - cache conversation

    Checks
    - ensure the booking transcript is sucessfully pulled out of the twilio platform. 
    - check the path to the stored media  
    """
    booking = telehealth_booking

    twilio = Twilio()

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

@pytest.mark.skip
def test_telehealth_transcript_get(test_client, telehealth_booking):
    """

    """
    booking = telehealth_booking

    twilio = Twilio()

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
