from datetime import datetime, timedelta
import random

from flask import current_app
import requests
from sqlalchemy.sql.expression import or_, select
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import ChatGrant, VideoGrant
from twilio.rest import Client
from werkzeug.exceptions import BadRequest

from odyssey import db
from odyssey.api.lookup.models import LookupBookingTimeIncrements
from odyssey.api.telehealth.models import TelehealthBookings, TelehealthChatRooms, TelehealthMeetingRooms
from odyssey.api.user.models import User
from odyssey.utils.constants import ALPHANUMERIC, TELEHEALTH_BOOKING_TRANSCRIPT_EXPIRATION_HRS, TWILIO_ACCESS_KEY_TTL


class Twilio():

    def __init__(self) -> None:
        self.twilio_credentials = self.grab_twilio_credentials()
        self.client = Client(self.twilio_credentials['api_key'], 
                     self.twilio_credentials['api_key_secret'],
                     self.twilio_credentials['account_sid'])
        self.conversation_service_sid = current_app.config['CONVERSATION_SERVICE_SID']  

    @staticmethod
    def grab_twilio_credentials():
        """
        Helper funtion to bring up twilio credentials for API acces.
        Raises an error if one or more of the credentials are None
        """
        twilio_account_sid = current_app.config['TWILIO_ACCOUNT_SID']
        twilio_api_key_sid = current_app.config['TWILIO_API_KEY_SID']
        twilio_api_key_secret = current_app.config['TWILIO_API_KEY_SECRET']

        if any(x is None for x in [twilio_account_sid,twilio_api_key_sid,twilio_api_key_secret]):
            raise BadRequest("Twilio API credentials have not been configured")

        return {'account_sid':twilio_account_sid,
                'api_key': twilio_api_key_sid,
                'api_key_secret': twilio_api_key_secret}


    def get_conversation_messages(self, conversation_sid: str):
        """
        Brings up the full conversation using the conversation_sid and twilio's API

        Parameters
        ----------
        conversation_sid : int
            Twilio's id for the conversation. 

        Returns
        -------
        list(dict)
            list of transcripts
        """
        transcript = []

        # response from API is a list of message objects
        messages = self.client.conversations \
                 .conversations(conversation_sid) \
                 .messages \
                 .list()
        # construct response with just the necessary details of each message
        for message in messages:
            transcript.append({
                'index': message.index,
                'body': message.body,
                'media': message.media,
                'author': message.author,
                'date_created': message.date_created,
                'date_updated': message.date_updated,
                'attributes': message.attributes
            })

        return transcript


    def get_booking_transcript(self, booking_id: int): 
        """
        Returns the full chat transcript for the bookings

        Parameters
        ----------
        booking_id : int
            Booking ID number

        Returns
        -------
        dict
            The transcript
        """

        # bring up the chat room 
        telehealth_chat = db.session.execute(select(TelehealthChatRooms
            ).where(TelehealthChatRooms.booking_id == booking_id)
            ).scalars().one_or_none()

        transcript = self.get_conversation_messages(telehealth_chat.conversation_sid)

        return transcript


    def create_twilio_access_token(self, modobio_id:str, meeting_room_name: str = None):
        """
        Generate a twilio access token for the provided modobio_id
        """
        if current_app.config['TESTING']:
            return (None, None)

        twilio_credentials = self.grab_twilio_credentials()
        token = AccessToken(twilio_credentials['account_sid'],
                        twilio_credentials['api_key'],
                        twilio_credentials['api_key_secret'],
                        identity=modobio_id,
                        ttl=TWILIO_ACCESS_KEY_TTL)

        token.add_grant(ChatGrant(service_sid=current_app.config['CONVERSATION_SERVICE_SID']))

        video_room_sid = None

        if meeting_room_name:
            room = db.session.execute(select(TelehealthMeetingRooms)\
                .where(TelehealthMeetingRooms.room_name == meeting_room_name)).scalars().one_or_none()
            
            if not room:
                room = self.client.video.rooms.create(unique_name=meeting_room_name)
            
            video_room_sid = room.sid            
            token.add_grant(VideoGrant(room=meeting_room_name))

        return (token.to_jwt(), video_room_sid)

    @staticmethod
    def generate_meeting_room_name(meeting_type: str = 'TELEHEALTH'):
        """ Generates unique, internally used names for meeting rooms.

        Parameters
        ----------
        meeting_type : str
            Meeting types will be either TELEHEALTH or CHATROOM
        """
        _hash = "".join([random.choice(ALPHANUMERIC) for i in range(15)])

        return (meeting_type+'_'+_hash).upper()

    def create_conversation(self, staff_user_id: int, client_user_id: int):
        """
        Name and create a conversation room on the twilio platform. Adds the users by their modobio_id
        
        Parameters
        ----------
        staff_user_id : int
            user_id of staff participant

        client_user_id : int
            user_id of client participant

        Returns
        -------
        int
            twilio's id for referencing the conversation instance
        """
        
        room_name = self.generate_meeting_room_name(meeting_type='CHATROOM')

        # create conversation through twilio api, add participants by modobio_id
        # TODO catch possible errors from calling Twilio
        conversation = self.client.conversations.conversations.create(
            friendly_name=room_name)

        # add both users to the conversation. We identify users externally using their modobio_id
        users = db.session.execute(
            select(User.modobio_id).
            where(User.user_id.in_([staff_user_id, client_user_id]))
        ).scalars().all()

        for modobio_id in users:
            conversation.participants.create(identity=modobio_id)

        return conversation.sid

    def create_telehealth_chatroom(self, booking_id: int):
        """
        Provision a telehealth chatroom using the twilio API. Store chatroom details in 
        the TelehealthChatrooms table

        Parameters
        ----------
        booking_id : int
            TelehealthBookings.idx for bringing up booking details.

        Returns
        -------
        int
            Conversation ID number
        """
        # bring up the booking
        booking = db.session.execute(select(TelehealthBookings
        ).where(TelehealthBookings.idx == booking_id)).scalars().one_or_none()

        new_chat_room = TelehealthChatRooms(
            staff_user_id=booking.staff_user_id,
            client_user_id=booking.client_user_id,
            booking_id = booking_id)
        
        conversation_sid = self.create_conversation(booking.staff_user_id, booking.client_user_id)

        # create chatroom entry into DB
        new_chat_room.conversation_sid = conversation_sid
        booking_end_time = LookupBookingTimeIncrements.query.get(booking.booking_window_id_end_time_utc).end_time
        new_chat_room.write_access_timeout = datetime.combine(booking.target_date_utc, booking_end_time) + timedelta(hours=TELEHEALTH_BOOKING_TRANSCRIPT_EXPIRATION_HRS)
        db.session.add(new_chat_room)

        return conversation_sid

    def send_message(self, user_id: int, conversation_sid: str, message_body: str=None, media_sid: str=None):
        """
        Add a message to the conversation on behalf of the user in user_id. 

        User must already be a conversation participant. 

        Parameters
        ----------
        user_id : int
            conversation participant

        conversation_sid : str
            twilio id for the conversation to be deleted

        message_body : str
            message text

        media_sid : str
            sid of the media file attached to this message        
        """
        user = db.session.execute(select(User).where(User.user_id == user_id)).scalars().one_or_none()
       
        # ensure user is a conversation participant
        chat_room = db.session.execute(select(TelehealthChatRooms
            ).where(TelehealthChatRooms.conversation_sid == conversation_sid
            ).where(or_(
                TelehealthChatRooms.staff_user_id == user_id,
                TelehealthChatRooms.client_user_id == user_id))).scalars().one_or_none()
       
        if not chat_room or not user:
          raise BadRequest("cannot find conversation or user not a conversation participant")
        
        try:
            self.client.conversations \
                    .conversations(conversation_sid) \
                    .messages \
                    .create(author= user.modobio_id, body=message_body, media_sid=media_sid)
        except Exception as e:
            # intended to catch errors when message is sent to a closed conversation
            raise e
        
    def delete_conversation(self, conversation_sid: str):
        """
        Delete the conversation refereced by the `conversation_sid`

        Parameters
        ----------
        conversation_sid : str
            twilio id for the conversation to be deleted
        """
        self.client.conversations.conversations(conversation_sid).delete()

    def complete_telehealth_video_room(self, booking_id: int):
        """
        Update the video room state to completed

        Parameters
        ----------
        booking_id : int
            The booking ID number
        """
        room = db.session.execute(
            select(TelehealthMeetingRooms
            ).where(TelehealthMeetingRooms.booking_id==booking_id)
        ).scalars().one_or_none()

        if room and room.sid:
            room_sid = room.sid
            t_room = self.client.video.rooms(room_sid).fetch()

            if t_room.status == 'in-progress':
                t_room.update(status='completed')

    def close_telehealth_chatroom(self, booking_id):
        """
        Update the conversation state to closed
        
        Parameters
        ----------
        booking_id : int
            The booking ID number
        """
        # bring up the chat room 
        telehealth_chat = db.session.execute(select(TelehealthChatRooms
            ).where(TelehealthChatRooms.booking_id == booking_id)
            ).scalars().one_or_none()

        self.client.conversations \
                     .conversations(telehealth_chat.conversation_sid) \
                     .update(state='closed')

    def get_media(self, media_sid: str):
        """
        Retrieve a media url from 

        Parameters
        ----------
        media_sid : str
            A media ID

        Returns
        -------
        str
            contents of image download
        """
        response = requests.get(f"https://mcs.us1.twilio.com/v1/Services/{self.conversation_service_sid}/Media/{media_sid}/Content", 
                            auth = (self.twilio_credentials['api_key'], self.twilio_credentials['api_key_secret']),
                            stream=True)
        # TODO: log this
        try:
            response.raise_for_status()
        except Exception as e:
            raise BadRequest(message=response.json())                    

        return response.content
    
    
    def upload_media(self, media_path: str, content_type: str = 'image/jpeg'):
        """
        Upload a media file to twilio. Twilio responds with details on the media object they store on their end. We can use the sid in the response to 
        add the media file to a conversation. 

        Note: this is only used for testing

        Parameters
        ----------
        media_path : str
            relative path to media file

        Returns
        -------
        str
            The media ID number
        """
        with open(media_path, 'rb') as f:
            data = f.read()
    
        response = requests.post(f"https://mcs.us1.twilio.com/v1/Services/{self.conversation_service_sid}/Media", 
                            auth = (self.twilio_credentials['api_key'], self.twilio_credentials['api_key_secret']),
                            headers={'Content-Type': content_type},
                            data=data)
        try:
            response.raise_for_status()
        except Exception as e:
            raise BadRequest(response.text)                    

        return response.json()['sid']
