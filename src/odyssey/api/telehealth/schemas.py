import logging
logger = logging.getLogger(__name__)

from marshmallow import (
    Schema, 
    fields, 
    post_load,
    validate
)
from pytz import timezone
import pytz
from twilio.jwt import access_token
from twilio.rest.conversations.v1 import conversation

from odyssey import ma
from odyssey.api.telehealth.models import (
    TelehealthChatRooms,
    TelehealthBookingStatus,
    TelehealthBookings,
    TelehealthQueueClientPool,
    TelehealthStaffAvailability,
    TelehealthMeetingRooms,
    TelehealthQueueClientPool,
    TelehealthBookingDetails,
    TelehealthStaffSettings
)
from odyssey.api.user.models import User
from odyssey.utils.constants import DAY_OF_WEEK, GENDERS, BOOKINGS_STATUS, ACCESS_ROLES, USSTATES_2

class TelehealthBookingMeetingRoomsTokensSchema(Schema):
    twilio_token = fields.String()
    conversation_sid = fields.String()

class TelehealthTimeSelectSchema(Schema):
    staff_user_id = fields.Integer()
    start_time = fields.Time()
    end_time = fields.Time()
    booking_window_id_start_time = fields.Integer()
    booking_window_id_end_time = fields.Integer()
    target_date = fields.Date()

class TelehealthTimeSelectOutputSchema(Schema):
    appointment_times = fields.Nested(TelehealthTimeSelectSchema(many=True),missing=[])
    total_options = fields.Integer()

class TelehealthBookingStatusSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TelehealthBookingStatus
        exclude = ('idx',)
        include_fk = True

class TelehealthBookingsPUTSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TelehealthBookings

    payment_method_id = fields.Integer(required=False)    
    status = fields.String(required=False,validate=validate.OneOf(BOOKINGS_STATUS))

class TelehealthChatRoomsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TelehealthChatRooms
        exclude = ('booking', 'booking_id', 'client_user_id', 'staff_user_id')
    
    transcript_url = fields.String(missing=None)
    
class TelehealthUserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('email_verified','is_client','created_at','updated_at',\
            'modobio_id','is_staff','phone_number','deleted','email','is_internal')

    profile_picture = fields.String()
    start_time_localized = fields.Time()
    end_time_localized = fields.Time()
    timezone = fields.String()

class TelehealthBookingsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TelehealthBookings
        exclude = ('client_user_id',
        'staff_user_id',
        'idx', 
        'booking_window_id_start_time_utc',
        'booking_window_id_end_time_utc', 
        'created_at',
        'updated_at')
        include_fk = True

    booking_id = fields.Integer(dump_only=True)
    status = fields.String(required=False,validate=validate.OneOf(BOOKINGS_STATUS))
    status_history = fields.Nested(TelehealthBookingStatusSchema(many=True), dump_only=True)
    chat_room = fields.Nested(TelehealthChatRoomsSchema(only=['conversation_sid', 'room_name', 'room_status', 'transcript_url']), dump_only=True)
    client = fields.Nested(TelehealthUserSchema, dump_only=True)
    practitioner = fields.Nested(TelehealthUserSchema, dump_only=True)
    payment_method_id = fields.Integer(required=False)
    client_location_id = fields.Integer(required=False)
    start_time_utc = fields.Time()
    booking_url = fields.String()
    consult_rate = fields.Number(missing=None)

    @post_load
    def make_object(self, data, **kwargs):
        return TelehealthBookings(**data)

class TelehealthBookingsOutputSchema(Schema):
    bookings = fields.Nested(TelehealthBookingsSchema(many=True),missing=[])
    all_bookings = fields.Integer()  
    twilio_token = fields.String()

class TelehealthStaffAvailabilitySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TelehealthStaffAvailability
        exclude = ('created_at',)
        dump_only = ('idx', )    
        include_fk = True
    user_id = fields.Integer()
    booking_window_id = fields.Integer()    
    @post_load
    def make_object(self, data, **kwargs):
        return TelehealthStaffAvailability(**data)  

class TelehealthStaffAvailabilityInputSchema(Schema):
    """
    Schema represents input of staff availability for a time block within a day of the week
    """
    day_of_week = fields.String(validate=validate.OneOf(DAY_OF_WEEK))
    start_time = fields.Time()
    end_time = fields.Time()
 
class TelehealthStaffSettingsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TelehealthStaffSettings
        include_fk = True
        dump_only = ('user_id',)
        exclude = ('created_at', 'updated_at',)

    auto_confirm = fields.Boolean(required=True, metadata={'description':'auto-confirm appointments based on availability'})
    timezone = fields.String(validate=validate.OneOf(pytz.common_timezones),metadata={'description': 'optional timezone selection, defaults to UTC'}, missing='UTC')

    @post_load
    def make_object(self, data, **kwargs):
        return TelehealthStaffSettings(**data) 

class TelehealthStaffAvailabilityOutputSchema(Schema):
    availability = fields.Nested(TelehealthStaffAvailabilityInputSchema(many=True), missing=[])
    settings = fields.Nested(TelehealthStaffSettingsSchema, required=True)

class TelehealthMeetingRoomSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for TelehealthMeeting rooms model
    """    
    class Meta:
        model = TelehealthMeetingRooms
        exclude = ('created_at', 'updated_at', 'staff_access_token', 'client_access_token')

    access_token = fields.String(metadata={'description':'meeting room access token. To be shown only to the owner'}, required=False)
    conversation_sid = fields.String(metadata={'description':'chat room sid'}, required=False)
    
class TelehealthQueueClientPoolSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TelehealthQueueClientPool
        exclude = ('created_at', 'updated_at')
        dump_only = ('idx', 'user_id', 'location_name')
    
    duration = fields.Integer(missing=20)
    medical_gender = fields.String(validate=validate.OneOf([gender[0] for gender in GENDERS]),metadata={'description': 'Preferred Medical Professional gender'})
    timezone = fields.String(validate=validate.OneOf(pytz.common_timezones),metadata={'description': 'optional timezone selection, defaults to UTC'}, missing='UTC')
    location_name = fields.String()
    location_id = fields.Integer(required=True)
    payment_method_id = fields.Integer(required=True, metadata={'description': 'idx from PaymentMethods selected'})
    profession_type = fields.String(validate=validate.OneOf(ACCESS_ROLES), required=True)

    @post_load
    def make_object(self, data, **kwargs):
        return TelehealthQueueClientPool(**data)    

class TelehealthQueueClientPoolOutputSchema(Schema):
    queue = fields.Nested(TelehealthQueueClientPoolSchema(many=True),missing=[],metadata={'description':'SORTED queue of client pool'})
    total_queue = fields.Integer()

class TelehealthBookingDetailsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TelehealthBookingDetails
        exclude = ('created_at', 'updated_at')
        include_fk = True

class TelehealthBookingDetailsGetSchema(Schema):
    details = fields.String()
    images = fields.String()
    voice = fields.String()
    
class TelehealthChatRoomAccessSchema(Schema):
    """
    Validates response for telehealth chat room access request
    """

    access_token = fields.String()
    conversation_sid = fields.String()


class TelehealthConversationsSchema(Schema):
    conversation_sid = fields.String()
    booking_id = fields.Integer()
    staff_user_id = fields.Integer()
    staff_fullname = fields.String()
    client_user_id = fields.Integer()
    client_fullname = fields.String()

class TelehealthConversationsNestedSchema(Schema):

    conversations = fields.Nested(TelehealthConversationsSchema(many=True))
    twilio_token = fields.String()

class TelehealthTransciptMedia(Schema):
    """
    Nests media file details when returning telehelath transcripts
    """
    category = fields.String()
    filename = fields.String()
    content_type = fields.String() # MIME type
    media_link = fields.String() # temp link to media on s3

class TelehealthTranscriptsMessage(Schema):
    """
    Schema for indivisual messages as part of a telehealth transcipt stored on the modobio end. 
    """
    media = fields.Nested(TelehealthTransciptMedia(many=True))
    index = fields.Integer()
    body = fields.String()
    author = fields.String()
    attributes = fields.String()
    date_created = fields.DateTime()
    date_updated = fields.DateTime()

class TelehealthTranscriptsSchema(Schema):
    """
    Telehealth transcript response for stored transcipts
    """
    booking_id = fields.Integer()
    transcript = fields.Nested(TelehealthTranscriptsMessage(many=True))