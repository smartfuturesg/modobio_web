from marshmallow import (
    Schema, 
    fields, 
    post_load,
    validate
)
from twilio.jwt import access_token
from twilio.rest.conversations.v1 import conversation

from odyssey import ma
from odyssey.api.telehealth.models import (
    TelehealthBookings,
    TelehealthQueueClientPool,
    TelehealthStaffAvailability,
    TelehealthMeetingRooms,
    TelehealthQueueClientPool
)
from odyssey.utils.constants import DAY_OF_WEEK, GENDERS

class TelehealthTimeSelectSchema(Schema):
    staff_user_id = fields.Integer()
    start_time = fields.Time()
    end_time = fields.Time()

class TelehealthTimeSelectOutputSchema(Schema):
    appointment_times = fields.Nested(TelehealthTimeSelectSchema(many=True),missing=[])
    total_options = fields.Integer()

class TelehealthBookingsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TelehealthBookings
        dump_only = ('idx', 'client_user_id','staff_user_id',)
        include_fk = True

    # booking_window_id_start_time = fields.Integer()
    # booking_window_id_end_time = fields.Integer()

    @post_load
    def make_object(self, data, **kwargs):
        return TelehealthBookings(**data)

class TelehealthBookingsOutputSchema(Schema):
    bookings = fields.Nested(TelehealthBookingsSchema(many=True),missing=[])
    all_bookings = fields.Integer()  

class TelehealthStaffAvailabilitySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TelehealthStaffAvailability
        exclude = ('created_at',)
        dump_only = ('idx', )    

    user_id = fields.Integer()
    booking_window_id = fields.Integer()    
    @post_load
    def make_object(self, data, **kwargs):
        return TelehealthStaffAvailability(**data)  

class TelehealthStaffAvailabilityInputSchema(Schema):
    # class Meta:
    #     model = TelehealthStaffAvailability
    #     exclude = ('created_at',)
    #     dump_only = ('idx', 'user_id','booking_window_id')

    day_of_week = fields.String(validate=validate.OneOf(DAY_OF_WEEK))
    start_time = fields.Time()
    end_time = fields.Time()
    # @post_load
    # def make_object(self, data, **kwargs):
    #     return TelehealthStaffAvailability(**data)  

class TelehealthStaffAvailabilityOutputSchema(Schema):
    availability = fields.Nested(TelehealthStaffAvailabilityInputSchema(many=True), missing=[])

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
        dump_only = ('idx', 'user_id')
    
    duration = fields.Integer(missing=20)
    medical_gender = fields.String(validate=validate.OneOf([gender[0] for gender in GENDERS]),metadata={'description': 'Preferred Medical Professional gender'})

    @post_load
    def make_object(self, data, **kwargs):
        return TelehealthQueueClientPool(**data)    

class TelehealthQueueClientPoolOutputSchema(Schema):
    queue = fields.Nested(TelehealthQueueClientPoolSchema(many=True),missing=[],metadata={'description':'SORTED queue of client pool'})
    total_queue = fields.Integer()

class TelehealthChatRoomAccessSchema(Schema):
    """
    Validates response for telehealth chat room access request
    """

    access_token = fields.String()
    conversation_sid = fields.String()
