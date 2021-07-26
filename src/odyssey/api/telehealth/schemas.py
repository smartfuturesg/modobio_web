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
    TelehealthBookings,
    TelehealthQueueClientPool,
    TelehealthStaffAvailability,
    TelehealthMeetingRooms,
    TelehealthQueueClientPool,
    TelehealthBookingDetails,
    TelehealthStaffSettings
)
from odyssey.utils.constants import DAY_OF_WEEK, GENDERS, BOOKINGS_STATUS, ACCESS_ROLES

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

class TelehealthBookingsPUTSchema(Schema):
    booking_id = fields.Integer()

class TelehealthBookingsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TelehealthBookings
        dump_only = ('idx', 'client_user_id','staff_user_id')
        exclude = ('booking_window_id_start_time_utc','booking_window_id_end_time_utc', 'target_date_utc')
        include_fk = True

    # booking_window_id_start_time = fields.Integer()
    # booking_window_id_end_time = fields.Integer()
    booking_id = fields.Integer(dump_only=True)
    start_time = fields.Time(dump_only=True)
    end_time = fields.Time(dump_only=True)
    start_time_localized = fields.Time(dump_only=True)
    end_time_localized = fields.Time(dump_only=True)
    status = fields.String(required=False,validate=validate.OneOf(BOOKINGS_STATUS))
    conversation_sid = fields.String(dump_only=True)
    client_first_name = fields.String(dump_only=True)
    client_middle_name = fields.String(dump_only=True)
    client_last_name = fields.String(dump_only=True)
    staff_first_name = fields.String(dump_only=True)
    staff_middle_name = fields.String(dump_only=True)
    staff_last_name = fields.String(dump_only=True)
    timezone = fields.String(metadata={'description': 'timezone setting of the booking for the logged in user'})
    payment_method_id = fields.Integer(required=False)
    client_location_id = fields.Integer(required=False)
    client_profile_picture = fields.String(dump_only=True, metadata={'description': 'profile pic of client telehealth attendee'})
    staff_profile_picture = fields.String(dump_only=True, metadata={'description': 'profile pic of staff telehealth attendee'})

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

    auto_confirm = fields.Boolean(required=False, metadata={'description':'auto-confirm appointments based on availability'})
    timezone = fields.String(validate=validate.OneOf(pytz.common_timezones),metadata={'description': 'optional timezone selection, defaults to UTC'}, missing='UTC')

    @post_load
    def make_object(self, data, **kwargs):
        return TelehealthStaffSettings(**data) 

class TelehealthStaffAvailabilityOutputSchema(Schema):
    availability = fields.Nested(TelehealthStaffAvailabilityInputSchema(many=True), missing=[])
    settings = fields.Nested(TelehealthStaffSettingsSchema, missing=[])

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