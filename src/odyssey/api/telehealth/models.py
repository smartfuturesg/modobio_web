
from enum import unique
import random

from datetime import datetime
from sqlalchemy import text
from odyssey.utils.constants import ALPHANUMERIC, DB_SERVER_TIME
from odyssey import db

"""
Database models for all things telehealth. These tables will be used to keep track of bookings,
meeting rooms, and other data related to telehealth meetings
"""

class TelehealthMeetingRooms(db.Model):
    """ 
    Meeting room details for one-on-one meetings between clients and medical professionals.
    Details from Twilio will be stored here, including: session identifiers, meeting access tokens 
    for both participants, and the unique room name
    """

    __tablename__ = 'TelehealthMeetingRooms'

    created_at = db.Column(db.DateTime, server_default=text('clock_timestamp()'))
    """
    timestamp for when object was created. DB server time is used. 

    :type: :class:`datetime.datetime`
    """

    updated_at = db.Column(db.DateTime, server_default=text('clock_timestamp()'))
    """
    Last update timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    room_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    autoincrementing primary key representing the internal id of the room

    :type: int, primary key, autoincrement
    """

    room_name = db.Column(db.String)
    """
    Name of room assigned internally and given to Twilio API.

    :type: str
    """

    room_status = db.Column(db.String)
    """
    Status of meeting room to be updated by Twilio

    :type: str
    """

    client_user_id  = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)
    """
    user_id of the client participant

    :type: int
    """

    staff_user_id  = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)
    """
    user_id of the staff participant

    :type: int
    """

    client_access_token = db.Column(db.String)
    """
    Token provied by Twilio which grants access to the chat room

    :type: str
    """

    staff_access_token = db.Column(db.String)
    """
    Token provied by Twilio which grants access to the chat room
    """

    def generate_meeting_room_name(self, meeting_type = 'TELEHEALTH'):
        """ Generate the user's mdobio_id.

        The modo bio identifier is used as a public user id, it
        can also be exported to other healthcare providers (clients only).
        It is made up of the firstname and lastname initials and 10 random alphanumeric
        characters.

        Parameters
        ----------
        firstname : str
            Client first name.

        lastname : str
            Client last name.

        user_id : int
            User ID number.

        Returns
        -------
        str
            Medical record ID
        """
        _hash = "".join([random.choice(ALPHANUMERIC) for i in range(15)])
        self.room_name = (meeting_type+'_'+_hash).upper()
        return 

class TelehealthQueueClientPool(db.Model):
    """ 
    Holds all of the clients in a pool for their appointments. 
    This is used for BEFORE they are accepted and see their medical professional.
    """

    __tablename__ = 'TelehealthQueueClientPool'

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    timestamp for when object was created. DB server time is used. 

    :type: datetime
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    timestamp for when object was updated. DB server time is used. 

    :type: datetime
    """

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Auto incrementing primary key

    :type: int, primary key
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False)
    """
    Id of the user that this notification belongs to

    :type: int, foreign key('User.user_id')
    """

    profession_type = db.Column(db.String)
    """
    TODO: Change this to a relationship with the type of professional ID
    Professional type is used for what type of professional the client wants to meet with

    :type: str
    """

    target_date = db.Column(db.DateTime)
    """
    target date is the date that the client wants for their appointment

    :type: datetime
    """

    priority = db.Column(db.Boolean)
    """
    priority is a flag most likely set by the system admin, default is false.

    :type: bool
    """

    timezone = db.Column(db.String)
    """
    timezone the client is in

    :type: str
    """

    duration = db.Column(db.Integer)
    """
    3/3/2021, initially, we will default this to 20 minutes. 

    :type: int
    """

    medical_gender = db.Column(db.String)
    """
    preferred gender of the medical professional

    options: male, female, no-preference

    :type: str
    """