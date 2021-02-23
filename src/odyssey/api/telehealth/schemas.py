from marshmallow import Schema, fields, post_load, validate

from odyssey import ma
from odyssey.api.telehealth.models import (
    TelehealthQueueClientPool,
    TelehealthStaffAvailability,
)

from odyssey.utils.constants import DAY_OF_WEEK


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

class TelehealthQueueClientPoolSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TelehealthQueueClientPool
        exclude = ('created_at', 'updated_at')
        dump_only = ('idx', 'user_id')
    
    @post_load
    def make_object(self, data, **kwargs):
        return TelehealthQueueClientPool(**data)    

class TelehealthQueueClientPoolOutputSchema(Schema):
    queue = fields.Nested(TelehealthQueueClientPoolSchema(many=True),missing=[],description='SORTED queue of client pool')
    total_queue = fields.Integer()
