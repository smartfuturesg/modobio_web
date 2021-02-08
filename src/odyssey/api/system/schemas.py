from marshmallow import Schema, fields, post_load, validate

from odyssey import ma
from odyssey.api.system.models import (
    SystemTelehealthSettings
)

from odyssey.utils.constants import ACCESS_ROLES

class SystemTeleheathCostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SystemTelehealthSettings

    profession_type = fields.String(validate=validate.OneOf(ACCESS_ROLES))

    @post_load
    def make_object(self, data, **kwargs):
        return SystemTelehealthSettings(**data)

class SystemTelehealthSettingsSchema(Schema):
    
    costs = fields.Nested(SystemTeleheathCostSchema,
                            missing={}, 
                            description="Used when changing session costs for professions/territories")
    session_duration = fields.Integer()
    booking_notice_window = fields.Integer()