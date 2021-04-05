from marshmallow import Schema, fields, post_load, validate

from odyssey import ma
from odyssey.api.system.models import SystemTelehealthSessionCosts, SystemVariables

from odyssey.utils.constants import ACCESS_ROLES

class SystemTeleheathCostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SystemTelehealthSessionCosts
        exclude = ('created_at', 'updated_at')
        dump_only = ('session_min_cost', 'session_max_cost', 'cost_id')

    profession_type = fields.String(validate=validate.OneOf(ACCESS_ROLES))

    #decimal fields are not json serializable
    session_cost = fields.String()
    session_min_cost = fields.String()
    session_max_cost = fields.String()

    @post_load
    def make_object(self, data, **kwargs):
        return SystemTelehealthSessionCosts(**data)

class SystemTelehealthSettingsSchema(Schema):
    
    costs = fields.Nested(SystemTeleheathCostSchema(many=True),
                            missing={},
                            description="Used when changing session costs for professions/territories")
    session_duration = fields.Integer(validate=validate.Range(min=10, max=60))
    booking_notice_window = fields.Integer(validate=validate.Range(min=8, max=24))
    confirmation_window = fields.Float(validate=validate.Range(min=1.0, max=24.0))

class SystemVariablesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SystemVariables
        exclude = ('created_at', 'updated_at')

    @post_load
    def make_object(self, data, **kwargs):
        return SystemVariables(**data)