from marshmallow import Schema, fields

from odyssey import ma
from odyssey.api.user.models import User
from odyssey.api.wearable.models import Wearables, WearablesOura, WearablesFreeStyle

"""
  Schemas for the wearables API
"""
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