from marshmallow import (
    Schema, 
    fields, 
    post_load,
)

from odyssey import ma
from odyssey.api.telehealth.models import (
  TelehealthMeetingRooms,
  TelehealthQueueClientPool
)

class TelehealthMeetingRoomSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for TelehealthMeeting rooms model
    """    
    class Meta:
        model = TelehealthMeetingRooms
        exclude = ('created_at', 'updated_at', 'staff_access_token', 'client_access_token')

    access_token = fields.String(description='meeting room access token. To be shown only to the owner', required=False)

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
