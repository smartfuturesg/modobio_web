import logging
logger = logging.getLogger(__name__)

from flask_restx.fields import String
from sqlalchemy import text, insert
from sqlalchemy.sql.expression import true
from odyssey.utils.constants import DB_SERVER_TIME
from odyssey import db
from odyssey.utils.base.models import BaseModel, BaseModelWithIdx, UserIdFkeyMixin, ReporterIdFkeyMixin
from odyssey.utils.auth import token_auth

"""
Database models for all things telehealth. These tables will be used to keep track of bookings,
meeting rooms, and other data related to telehealth meetings
"""


class TelehealthBookings(BaseModelWithIdx):
    """ 
    Holds all of the client and Staff bookings 
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

    client = db.relationship('User', uselist=False, foreign_keys='TelehealthBookings.client_user_id')
    """
    Many-to-One relationship with User

    :type: :class: `User` intance
    """

    practitioner = db.relationship('User', uselist=False, foreign_keys='TelehealthBookings.staff_user_id')
    """
    Many-to-One relationship with User

    :type: :class: `User` intance
    """

    profession_type = db.Column(db.String)
    """
    Profession type, IE: doctor, trainer, nutritionist, etc

    :type: str:
    """

    target_date = db.Column(db.Date, nullable=False)
    """
    target date is the date of the appointment in client's timezone

    :type: date
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

    status_history = db.relationship('TelehealthBookingStatus', uselist=True, back_populates='booking')
    """
    One-to-Many relationship with TelehealthBookingStatus, history of all statuses the booking has gone through.

    :type: :class:`TelehealthBookingStatus` instance list
    """

    status = db.Column(db.String)
    """
    Status of the booking

    :type: str
    """    

    client_timezone = db.Column(db.String)
    """
    Staff's timezone setting at the time of booking. 

    :type: str
    """

    staff_timezone = db.Column(db.String)
    """
    Staff's timezone setting at the time of booking. 

    :type: str
    """

    target_date_utc = db.Column(db.Date)
    """
    target date converted to utc

    :type: date
    """

    booking_window_id_start_time_utc = db.Column(db.Integer, db.ForeignKey('LookupBookingTimeIncrements.idx', ondelete="CASCADE"), nullable=False)
    """ 
    start time booking_window_id in UTC

    :type: int, foreign key('LookupBookingTimeIncrements.idx')
    """
    
    booking_window_id_end_time_utc = db.Column(db.Integer, db.ForeignKey('LookupBookingTimeIncrements.idx', ondelete="CASCADE"), nullable=False)
    """ 
    end time booking_window_id in UTC

    :type: int, foreign key('LookupBookingTimeIncrements.idx')
    """

    client_location_id = db.Column(db.Integer, db.ForeignKey('LookupTerritoriesOfOperations.idx'), nullable=False)
    """
    client location id for this booking
        :type: int, foreign key(LookupTerritoriesOfOperations.idx)
    """

    payment_method_id = db.Column(db.Integer, db.ForeignKey('PaymentMethods.idx'), nullable=True)
    """
    client payment method selected from PaymentMethods previously set up

    :type: int, foreign key(PaymentMethods.idx)
    """

    staff_calendar_id = db.Column(db.Integer, db.ForeignKey('StaffCalendarEvents.idx'), nullable=True)
    """
    Idx for the StaffCalendarEvents entry related to this booking.

    :type: int, foreign key(StaffCalendarEvents.idx)
    """

    charged = db.Column(db.Boolean, default=False)
    """
    Denotes if the system has attempted to charge the client for this bookings yet. Even if a charge
    is unsuccessful, this will be set to true to denote that the booking was attempted to be charged
    by the initial charge task.

    :type: boolean
    """
    
    notified = db.Column(db.Boolean, default=False)
    """
    Denotes if celery has already sent the notifications and ehr permissions for this booking.
    
    :type: boolean
    """

    uid = db.Column(db.String(36), nullable = True)
    """
    UUID of booking used for external reference.

    :type: str
    """
    
    chat_room = db.relationship('TelehealthChatRooms', uselist=False, back_populates='booking')
    """
    One-to_One relationship with TelehealthChatRooms

    :type: :class: `TelehealthChatRooms` instance
    """

    booking_details = db.relationship('TelehealthBookingDetails', uselist=False, back_populates='booking')
    """
    One-to_One relationship with TelehealthBookingDetails

    :type: :class: `TelehealthBookingDetails` instance
    """

    staff_calendar = db.relationship('StaffCalendarEvents', uselist=False)
    """
    One-to_One relationship with StaffCalendarEvents

    :type: :class: `StaffCalendarEvents` instance
    """

    medical_gender_preference = db.Column(db.String)
    """
    preferred gender of the medical professional

    options: male, female, no-preference

    :type: str
    """

    consult_rate = db.Column(db.Numeric(10,2))
    """
    Amount to be charged to the client. Based on the practitioner's hourly consult rate and the scheduled duration of the call.

    :type: Numeric
    """

    payment_history_id = db.Column(db.Integer, db.ForeignKey('PaymentHistory.idx'), nullable = True)
    """
    Foreign key to the PaymentHistory entry for this booking

    :type: int, foreignkey(PaymentHistory.idx)
    """

    scheduled_duration_mins = db.Column(db.Integer)
    """
    Duration of the telehealth appointment as scheduled. This is used for charging users based on the hourly rate specified by practitioners. 

    :type: int
    """

    payment_notified = db.Column(db.Boolean, default=False)
    """
    Denotes if celery has already sent the notification for this booking being charged. 
    Gets set to True when it has been.

    :type: boolean
    """


@db.event.listens_for(TelehealthBookings, "after_insert")
def add_booking_status_history(mapper, connection, target):
    """
    Listens for any new status change
    Updates the booking status history
    """
    current_user, _ = token_auth.current_user()
    booking = target
    
    connection.execute(
        insert(TelehealthBookingStatus),
        [
            {"status":booking.status,
            "booking_id":booking.idx,
            "reporter_id":current_user.user_id,
            "reporter_role":'Practitioner' if current_user.user_id == booking.staff_user_id else 'Client'}])

@db.event.listens_for(TelehealthBookings, "after_update", "status")
def update_booking_status_history(mapper, connection, target):
    """
    Listens for any new status change
    Updates the booking status history
    """
    try:
        current_user, _ = token_auth.current_user()
        current_user_id = current_user.user_id
    except:
        current_user_id = None

    try:
        booking = target.obj()
    except:
        booking = target
    
    if current_user_id:
        reporter_role = 'Practitioner' if current_user_id == booking.staff_user_id else 'Client'
    else:
        # if the status is updated through the task cleanup_unended_call or after a failed payment
        reporter_role = 'System'

    connection.execute(
        insert(TelehealthBookingStatus),
        [
            {"status":booking.status,
            "booking_id":booking.idx,
            "reporter_id":current_user_id,
            "reporter_role":reporter_role
            }])
    

class TelehealthBookingStatus(db.Model):
    """
    Holds all status changes a booking goes through
    """
    __tablename__ = 'TelehealthBookingStatus'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    booking_id = db.Column(db.Integer, db.ForeignKey('TelehealthBookings.idx', ondelete="CASCADE"), nullable=False)
    """
    booking_id is the idx of the booking from TelehealthBookings

    :type: int, foreign key('TelehealthBookings.idx')
    """

    booking = db.relationship("TelehealthBookings", uselist=False, back_populates='status_history', foreign_keys='TelehealthBookingStatus.booking_id')
    """
    Many-to-One relationship with TelehealthBookings, the full booking info object

    :type: :class:`TelehealthBookings` instance
    """
    reporter_id  = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=True)
    """
    Reporter ID number, foreign key to User.user_id

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
    """

    reporter_role = db.Column(db.String(30))
    """
    role of the user reporting the status, could be client or practitioner

    :type: str, max length 30
    """

    status = db.Column(db.String(20))
    """
    status of the booking, 
    should be one of constant BOOKINGS_STATUS = ('Pending', 'Accepted', 'Canceled', 'In Progress', 'Completed')

    :type: str, max length 20
    """

    time = db.Column(db.DateTime, server_default=DB_SERVER_TIME)
    """
    date and time when the booking status was updated to current status

    :type: :class:`datetime.datetime`
    """


class TelehealthMeetingRooms(BaseModel):
    """ 
    Meeting room details for one-on-one meetings between clients and medical professionals.
    Details from Twilio will be stored here, including: session identifiers, meeting access tokens 
    for both participants, and the unique room name
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

    sid = db.Column(db.String)
    """
    SID for the video room, it allows fetching the room and updating it.

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



class TelehealthStaffAvailability(BaseModelWithIdx):
    """ 
    Holds all of the clients in a pool for their appointments. 
    This is used for BEFORE they are accepted and see their medical professional.
    """

    user_id = db.Column(db.Integer, db.ForeignKey('TelehealthStaffSettings.user_id', ondelete="CASCADE"), nullable=False)
    """
    staff user id TelehealthStaffSettings Foreign key

    :type: int, foreign key('TelehealthStaffSettings.user_id')
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

    settings = db.relationship('TelehealthStaffSettings', uselist=False, back_populates='availability')
    """
    Many to one relationshp with TelehealthStaffSettings

    :type: :class:`TelehealthStaffSettings` instance
    """
    
class TelehealthStaffAvailabilityExceptions(BaseModelWithIdx, UserIdFkeyMixin):
    """
    Holds information for temporary availability exceptions
    """
    
    exception_date = db.Column(db.Date, nullable=False)
    """
    Date of this exception.
    
    :type: Datetime
    """
    
    exception_booking_window_id_start_time = db.Column(db.Integer, db.ForeignKey('LookupBookingTimeIncrements.idx', ondelete="CASCADE"), nullable=False)
    """
    Exception start time as a booking window id in refernce to UTC time.

    :type: int, foreign key('LookupBookingTimeIncrements.idx')
    """
    
    exception_booking_window_id_end_time = db.Column(db.Integer, db.ForeignKey('LookupBookingTimeIncrements.idx', ondelete="CASCADE"), nullable=False)
    """
    Exception end time as a booking window id in reference to UTC time.

    :type: int, foreign key('LookupBookingTimeIncrements.idx')
    """
    
    is_busy = db.Column(db.Boolean, nullable=False)
    """
    Denotes the types of exception. Exceptions can be 'busy' (true) meaning they remove blocks from
    normal availability or 'free' (false) meaning that add blocks to normal availability.
    
    :type: bool
    """
    
    label = db.Column(db.String(100))
    """
    An optional label placed on this exception to explain what the exception is for.
    
    :type: string(100)
    """


class TelehealthQueueClientPool(BaseModelWithIdx, UserIdFkeyMixin):
    """ 
    Holds all of the clients in a pool for their appointments. 
    This is used for BEFORE they are accepted and see their medical professional.
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

    location_id = db.Column(db.Integer, db.ForeignKey('LookupTerritoriesOfOperations.idx'), nullable=True)
    """
    client location id for this booking request
    :type: int, foreign key(LookupTerritoriesOfOperations.idx)
    """

    payment_method_id = db.Column(db.Integer, db.ForeignKey('PaymentMethods.idx'), nullable=True)
    """
    client payment method selected from PaymentMethods previously set up

    :type: int, foreign key(PaymentMethods.idx)
    """
    

class TelehealthBookingDetails(BaseModelWithIdx):
    """ 
    Table holding text, images or sound recording details about a booking
    """

    __table_args__ = (
        db.UniqueConstraint('booking_id', ),)


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

    images = db.Column(db.ARRAY(db.String(1024), dimensions=1), nullable=False, server_default='{}')
    """
    List of paths to images stored on S3.

    :type: list(str)
    """

    voice = db.Column(db.String(1024))
    """
    Path to voice recording stored on S3.

    :type: str
    """

    reason_id = db.Column(db.Integer, db.ForeignKey('LookupVisitReasons.idx'), nullable = True)
    """
    Foreign key to idx of VisitReasons, nullable

    :type: int, foreignkey(LookupVisitReasons.idx)
    """

    booking = db.relationship('TelehealthBookings', uselist=False, back_populates='booking_details')
    """
    One-to-One relationship with TelehealthBookings

    :type: :class:`TelehealthBookings` instance
    """


class TelehealthChatRooms(BaseModel):
    """ 
    Table stores details on chat rooms created through the Twiliio Conversations API.
    
    Unlike TelehealthMeetingRooms, there will be only one unique room created per
    client-staff pair. We do this so that chat threads persist through subsequent client and
    staff interactions. 

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

    booking = db.relationship('TelehealthBookings', uselist=False, back_populates='chat_room')
    """
    One-to-One relationship with TelehealthBookings

    :type: :class: `TelehalthBookings` instance
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

    transcript_object_id = db.Column(db.String)
    """
    Object id for telehealth transcript entry on mongo db

    :type: str
    """

    write_access_timeout = db.Column(db.DateTime)
    """
    Time write accesss to the conversation threaf will expire. After this time, the conversation will be cached on the modobio end
    and will be removed from twilio. 

    timezone is always in UTC
    
    :type: datetime
    """
    
class TelehealthStaffSettings(BaseModel):
    """
    Holds staff preferred settings for Telehealth appointments

    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), primary_key=True, nullable=False)
    """
    User ID number, foreign key to User.user_id

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
    """

    auto_confirm = db.Column(db.Boolean, server_default='t')
    """
    Setting to determine if Staff member wants to auto confirm appointments

    :type: bool
    """

    timezone = db.Column(db.String)
    """
    Staff's timezone setting for the current telehealth availability submisison

    :type: str
    """

    availability = db.relationship('TelehealthStaffAvailability', uselist=True, back_populates="settings")
    """
    One to many relationship with staff availability

    :type: :class:`TelehealthStaffAvailability` instance list
    """
