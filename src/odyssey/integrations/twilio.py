import os
import random

from flask import current_app
from sqlalchemy.sql.expression import or_, select
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import ChatGrant, VideoGrant
from twilio.rest import Client
from twilio.rest.conversations.v1 import conversation
from odyssey.api.telehealth.models import TelehealthBookings, TelehealthChatRooms

from odyssey import db
from odyssey.api.user.models import User
from odyssey.utils.constants import ALPHANUMERIC, TWILIO_ACCESS_KEY_TTL
from odyssey.utils.errors import InputError, MissingThirdPartyCredentials


class Twilio():

    def __init__(self) -> None:
        self.twilio_credentials = self.grab_twilio_credentials()
        self.client = Client(self.twilio_credentials['api_key'], 
                     self.twilio_credentials['api_key_secret'],
                     self.twilio_credentials['account_sid'])

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
            raise MissingThirdPartyCredentials(message="Twilio API credentials have not been configured")

        return {'account_sid':twilio_account_sid,
                'api_key': twilio_api_key_sid,
                'api_key_secret': twilio_api_key_secret}



    def get_conversation_messages(self, conversation_sid: str):
        """
        Brings up the full conversation using the conversation_sid and twilio's API

        Params
        ------
        conversation_sid: Twilio's id for the conversation. 

        Returns
        ------
        messages: Dict
        """

        messages = self.client.conversations \
                 .conversations(conversation_sid) \
                 .messages \
                 .list()


        return messages


    def get_booking_transcript(self, booking_id: int): 
        """
        Returns the full chat transcript for the bookings

        Params
        ------
        booking_id: TelehealthBookings.idx for the booking

        Returns
        ------
        messages: Dict
        """

        # bring up the chat room 
        telehealth_chat = db.session.execute(select(TelehealthChatRooms
        ).where(TelehealthChatRooms.booking_id == booking_id)
        ).scalars().one_or_none()

        messages = self.get_conversation_messages(telehealth_chat.conversation_sid)


    def create_twilio_access_token(self, modobio_id:str, meeting_room_name: str = None):
        """
        Generate a twilio access token for the provided modobio_id
        """
        if current_app.config['TESTING']:
            return

        twilio_credentials = self.grab_twilio_credentials()
        token = AccessToken(twilio_credentials['account_sid'],
                        twilio_credentials['api_key'],
                        twilio_credentials['api_key_secret'],
                        identity=modobio_id,
                        ttl=TWILIO_ACCESS_KEY_TTL)

        token.add_grant(ChatGrant(service_sid=current_app.config['CONVERSATION_SERVICE_SID']))

        if meeting_room_name:
            token.add_grant(VideoGrant(room=meeting_room_name))

        return token.to_jwt()

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
        
        Params
        ------
        staff_user_id: user_id of staff participant
        client_user_id: user_id of client participant

        Returns
        ------
        conversation_sid: twilio's id for referecing the conversation instance
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

        Params
        ------
        booking_id: TelehealthBookings.idx for bringing up booking details.

        Returns
        ------
        """
        # bring up the booking
        booking = db.session.execute(select(TelehealthBookings
        ).where(TelehealthBookings.idx == booking_id)).scalars().one_or_none()

        new_chat_room = TelehealthChatRooms(
            staff_user_id=booking.staff_user_id,
            client_user_id=booking.client_user_id,
            booking_id = booking_id)


        # create chatroom entry into DB
        new_chat_room.conversation_sid = conversation.sid
        db.session.add(new_chat_room)

        return conversation.sid

    def send_message(self, user_id: int, conversation_sid: str, message_body: str):
        """
        Add a message to the conversation on behalf of the user in user_id. 

        User must already be a conversation participant. 
        Params
        ------
        user_id: conversation participant
        conversation_sid: twilio id for the conversation to be deleted
        message_body: message text. 

        Returns
        ------
        None
        
        """
        user = db.session.execute(select(User).where(User.user_id == user_id)).scalars().one_or_none()
       
        # ensure user is a conversation participant
        chat_room = db.session.execute(select(TelehealthChatRooms
            ).where(TelehealthChatRooms.conversation_sid == conversation_sid
            ).where(or_(
                TelehealthChatRooms.staff_user_id == user_id,
                TelehealthChatRooms.client_user_id == user_id))).scalars().one_or_none()
       
        if not chat_room or not user:
          raise InputError(message="cannot find conversation or user not a conversation participant")
        

        self.client.conversations \
                .conversations(conversation_sid) \
                .messages \
                .create(author= user.modobio_id, body=message_body)
        
    def delete_conversation(self, conversation_sid: str):
        """
        Delete the conversation refereced by the `conversation_sid`

        Params
        ------
        conversation_sid: twilio id for the conversation to be deleted

        Returns
        ------
        None
        """

        self.client.conversations.conversations(conversation_sid).delete()

        return




