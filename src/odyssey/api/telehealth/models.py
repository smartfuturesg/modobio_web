
from sqlalchemy import text
from odyssey.utils.constants import DB_SERVER_TIME
from odyssey import db

"""
Database models for all things telehealth. These tables will be used to keep track of bookings,
meeting rooms, and other data related to telehealth meetings
"""

class TelehealthBookings(db.Model):
    """ 
    Holds all of the client and Staff bookings 
    """

    __tablename__ = 'TelehealthBookings'

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    timestamp for when object was created. DB server time is used. 

    :type: datetime
    """

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Auto incrementing primary key

    :type: int, primary key
    """

    client_user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False)
    """
    staff member id 

    :type: int, foreign key('User.user_id')
    """

    staff_user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False)
    """
    staff member id 

    :type: int, foreign key('User.user_id')
    """

    profession_type = db.Column(db.String)
    """
    Profession type, IE: doctor, trainer, nutritionist, etc

    :type: str:
    """

    target_date = db.Column(db.Date)
    """
    target date is the date of the appointment

    :type: datetime
    """

    booking_window_id_start_time = db.Column(db.Integer, db.ForeignKey('LookupBookingTimeIncrements.idx', ondelete="CASCADE"), nullable=False)
    """ 
    start time booking_window_id

    :type: int, foreign key('LookupBookingTimeIncrements.idx')
    """
    
    booking_window_id_end_time = db.Column(db.Integer, db.ForeignKey('LookupBookingTimeIncrements.idx', ondelete="CASCADE"), nullable=False)
    """ 
    end time booking_window_id
    :type: int, foreign key('LookupBookingTimeIncrements.idx')
    """

    status = db.Column(db.String)
    """
    Status of the booking

    :type: str
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
    autoincrementing primary key representing the internal id of the chat room. This is 
    seperate from the IDs that are assigned by twilio. 

    :type: int, primary key, autoincrement
    """

    booking_id = db.Column(db.Integer, db.ForeignKey('TelehealthBookings.idx', ondelete="CASCADE"), nullable=False)
    """
    booking_id is the idx of the booking from TelehealthBookings

    :type: int, foreign key('TelehealthBookings.idx')
    """
    room_name = db.Column(db.String)
    """
    Name of room assigned internally and given to Twilio API. When interacting with twilio, this name
    will be under the attribute `friendly_name`. We will use this in order to call up the room 
    from twilio for access grants and webhooks. 

    :type: str
    """

    room_status = db.Column(db.String)
    """
    Status of meeting room to be updated by Twilio.

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



class TelehealthStaffAvailability(db.Model):
    """ 
    Holds all of the clients in a pool for their appointments. 
    This is used for BEFORE they are accepted and see their medical professional.
    """

    __tablename__ = 'TelehealthStaffAvailability'

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    timestamp for when object was created. DB server time is used. 

    :type: datetime
    """

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Auto incrementing primary key

    :type: int, primary key
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False)
    """
    staff member id 

    :type: int, foreign key('User.user_id')
    """

    day_of_week = db.Column(db.String)
    """
    Day of the week

    :type: str
    """
    
    booking_window_id = db.Column(db.Integer, db.ForeignKey('LookupBookingTimeIncrements.idx', ondelete="CASCADE"), nullable=False)
    """
    booking window id

    :type: int, foreign key('LookupBookingTimeIncrements.idx')
    """

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

class TelehealthBookingDetails(db.Model):
    """ 
    Table holding text, images or sound recording details about a booking
    """

    __tablename__ = 'TelehealthBookingDetails'

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

    booking_id = db.Column(db.Integer, db.ForeignKey('TelehealthBookings.idx', ondelete="CASCADE"), nullable=False)
    """
    booking_id is the idx of the booking from TelehealthBookings

    :type: int, foreign key('TelehealthBookings.idx')
    """

    details = db.Column(db.String)
    """
    client details about a booked teleheath call
    :type: str
    """

    media = db.Column(db.String)
    """
    aws url link to media saved in S3 bucket (image or recording)
    :type: str
    """

class TelehealthChatRooms(db.Model):
    """ 
    Table stores details on chat rooms created through the Twiliio Conversations API.
    
    Unlike TelehealthMeetingRooms, there will be only one unique room created per
    client-staff pair. We do this so that chat threads persist through subsequent client and
    staff interactions. 

    """

    __tablename__ = 'TelehealthChatRooms'

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

    booking_id = db.Column(db.Integer, db.ForeignKey('TelehealthBookings.idx', ondelete="CASCADE"), nullable=False)
    """
    booking_id is the idx of the booking from TelehealthBookings

    :type: int, foreign key('TelehealthBookings.idx')
    """

    conversation_sid = db.Column(db.String)
    """
    Conversation SID form Twilio API. Format: CHXXX

    :type: str
    """

    room_name = db.Column(db.String)
    """
    Name of room assigned internally and given to Twilio API.

    :type: str
    """

    room_status = db.Column(db.String)
    """
    Status of chat room to be updated by Twilio.

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