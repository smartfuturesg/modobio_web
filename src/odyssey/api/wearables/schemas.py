""" Schemas for the wearables API """
import logging
logger = logging.getLogger(__name__)

from marshmallow import Schema, fields

from odyssey import ma
from odyssey.api.user.models import User
from odyssey.api.wearables.models import Wearables, WearablesFreeStyle


class WearablesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Wearables
        load_instance = True
        exclude = ('idx', 'user_id', 'created_at', 'updated_at')


# TODO: delete this schema when oura-old endpoint is removed.
class WearablesOuraAuthSchema(Schema):
    oura_client_id = fields.String()
    oauth_state = fields.String()


class WearablesOAuthGetSchema(Schema):
    url = fields.String(required=True)
    client_id = fields.String(required=True)
    redirect_uri = fields.String(required=True)
    response_type = fields.String(required=True)
    scope = fields.String(required=True)
    state = fields.String(required=True)


class WearablesOAuthPostSchema(Schema):
    code = fields.String(required=True)
    state = fields.String(required=True)
    redirect_uri = fields.String(required=True)
    scope = fields.String()


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



class WearablesSleepDataNested(Schema):
    """
    sleep data for one day 
    """
    hr_resting_bpm = fields.Float(default = 0)
    sleep_duration_seconds = fields.Integer(default = 0)
    in_bed_duration_seconds = fields.Integer(default = 0)
    bed_time_start = fields.String(default = '')
    bed_time_end = fields.String(default = '')

class WearablesVitalsDataNested(Schema):
    """
    sleep data for one day 
    """
    hr_resting_bpm = fields.Float(default = 0)
    respiratory_rate_bpm_avg = fields.Float(default = 0)
    hrv_seconds_avg = fields.Float(default = 0)
    body_temp_celsius = fields.Float(default = 0)

class WearablesActivityDataNested(Schema):
    """
    Activity data for one day
    """
    steps = fields.Integer(default = 0)

class WearablesCalorieDataNested(Schema):
    """
    Activity data for one day
    """
    calories_active = fields.Integer(default = 0)
    calories_total = fields.Integer(default = 0)
    calories_bmr = fields.Integer(default = 0)
class WearablesDataResponseNestedSchema(Schema):
    """
    Schema for each wearable data response item. Nests activity and sleep data
    """
    date = fields.String()
    activity = fields.Nested(WearablesActivityDataNested)
    sleep = fields.Nested(WearablesSleepDataNested)
    vitals = fields.Nested(WearablesVitalsDataNested)
    calories = fields.Nested(WearablesCalorieDataNested)

class WearablesDataResponseSchema(Schema):
    start_date = fields.String()
    end_date = fields.String()
    total_items = fields.Integer()
    items = fields.Nested(WearablesDataResponseNestedSchema(many=True))