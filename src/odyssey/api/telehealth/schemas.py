from marshmallow import (
    Schema, 
    fields, 
    post_load,
    validate
)

from odyssey import ma
from odyssey.api.telehealth.models import (
    TelehealthClientStaffBookings,
    TelehealthQueueClientPool,
    TelehealthStaffAvailability,
    TelehealthMeetingRooms,
    TelehealthQueueClientPool
)
from odyssey.utils.constants import DAY_OF_WEEK, GENDERS

class TelehealthClientStaffBookingsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TelehealthClientStaffBookings
        dump_only = ('idx', 'client_user_id','staff_user_id',)

    @post_load
    def make_object(self, data, **kwargs):
        return TelehealthClientStaffBookings(**data)

class TelehealthClientStaffBookingsOutputSchema(Schema):
    bookings = fields.Nested(TelehealthClientStaffBookingsSchema(many=True),missing=[])
    all_bookings = fields.Integer()  

class TelehealthStaffAvailabilitySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TelehealthStaffAvailability
        exclude = ('created_at',)
        dump_only = ('idx', 'staff_id')

    day_of_week = fields.String(validate=validate.OneOf(DAY_OF_WEEK))
    @post_load
    def make_object(self, data, **kwargs):
        return TelehealthStaffAvailability(**data)  

class TelehealthStaffAvailabilityOutputSchema(Schema):
    availability = fields.Nested(TelehealthStaffAvailabilitySchema(many=True), missing=[])

class TelehealthMeetingRoomSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for TelehealthMeeting rooms model
    """    
    class Meta:
        model = TelehealthMeetingRooms
        exclude = ('created_at', 'updated_at', 'staff_access_token', 'client_access_token')

    access_token = fields.String(metadata={'description':'meeting room access token. To be shown only to the owner'}, required=False)

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
