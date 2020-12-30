from marshmallow import Schema, fields

from odyssey import ma
from odyssey.api.user.models import User
from odyssey.api.wearables.models import LookUpActivityTrackers, Wearables, WearablesOura, WearablesFreeStyle

"""
  Schemas for the wearables API
"""

class WearablesLookUpActivityTrackersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookUpActivityTrackers

class WearablesLookUpActivityTrackersOutputSchema(Schema):
    items = fields.Nested(WearablesLookUpActivityTrackersSchema(many=True),missing=[])
    total_items = fields.Integer()

class WearablesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Wearables
        load_instance = True
        exclude = ('idx', 'user_id', 'created_at', 'updated_at')

class WearablesOuraAuthSchema(Schema):
    oura_client_id = fields.String()
    oauth_state = fields.String()


class WearablesFreeStyleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WearablesFreeStyle
        load_instance = True
        exclude = ('idx', 'user_id', 'created_at', 'updated_at')


class WearablesFreeStyleActivateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WearablesFreeStyle
        load_instance = True
        fields = ('activation_timestamp',)