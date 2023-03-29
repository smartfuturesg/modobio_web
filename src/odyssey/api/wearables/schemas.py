""" Schemas for the wearables API """
import logging
logger = logging.getLogger(__name__)

from datetime import datetime
from marshmallow import Schema, fields, EXCLUDE, post_dump, validate, pre_dump

from odyssey import ma
from odyssey.api.user.models import User
from odyssey.api.wearables.models import Wearables, WearablesFreeStyle


##############################
#
# V1 of the Wearables schemas.
#
##############################

# TODO: deprecated in V2 of the API. Remove when V1 of the API is no longer supported.

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

##############################
#
# V2 of the Wearables schemas.
#
##############################

import terra.api.api_responses

from marshmallow_dataclass import class_schema

from terra.models.v2.activity import Activity
from terra.models.v2.athlete import Athlete
from terra.models.v2.body import Body
from terra.models.v2.daily import Daily
from terra.models.v2.menstruation import Menstruation
from terra.models.v2.nutrition import Nutrition
from terra.models.v2.sleep import Sleep
from terra.models.user import User

class WearablesV2BaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        load_only = ('status', 'user_id')

# Automatically convert all Terra classes to marshmallow schemas.
# Terra defines all responses as dataclasses.dataclass. Use the
# module marshmallow_dataclass to convert those directly to
# marshmallow schemas.

# API response classes
for response_class_name in terra.api.api_responses.__all__:
    response_class = getattr(terra.api.api_responses, response_class_name)
    response_schema = class_schema(response_class, WearablesV2BaseSchema)
    globals()[f'WearablesV2{response_class_name}Schema'] = response_schema

# Data classes
WearablesV2ActivitySchema = class_schema(Activity, WearablesV2BaseSchema)
WearablesV2AthleteSchema = class_schema(Athlete, WearablesV2BaseSchema)
WearablesV2BodySchema = class_schema(Body, WearablesV2BaseSchema)
WearablesV2DailySchema = class_schema(Daily, WearablesV2BaseSchema)
WearablesV2MenstruationSchema = class_schema(Menstruation, WearablesV2BaseSchema)
WearablesV2NutritionSchema = class_schema(Nutrition, WearablesV2BaseSchema)
WearablesV2SleepSchema = class_schema(Sleep, WearablesV2BaseSchema)
WearablesV2UserSchema = class_schema(User, WearablesV2BaseSchema)

# Add extra field
WearablesV2UserAuthUrlSchema = WearablesV2UserAuthUrlSchema.from_dict({'token': fields.String(default=None)})


# Additional schemas
class WearablesV2UserGetSchema(Schema):
    wearables = fields.List(fields.String(), dump_default=[])


class WearablesV2ProvidersGetSchema(Schema):
    providers = fields.Dict(keys=fields.String(), values=fields.String())
    sdk_providers = fields.Dict(keys=fields.String(), values=fields.String())

class WearablesV2UserDataSchema(Schema):
    user_id = fields.Integer()
    wearable = fields.String()
    timestamp = fields.DateTime(format='%Y-%m-%dT%H:%M:%S%z')
    data = fields.Dict()

    @pre_dump
    def handle_datetime_fields(self, data, **kwargs):
        """
        Converts datetime objects to the string representation in the 'data' 
        part of the mongo documents in order to serialize the object correctly
        """
        result = self.convert_datetime(data['data'])
        data['data'] = result
        return data

    def convert_datetime(self, data):
        """
        Recursive function that iterates through nested dictionaries and 
        replaces datetime object with string time format. 
        """
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = datetime.isoformat(value)
            elif isinstance(value, dict):
                self.convert_datetime(data[key])
            elif isinstance(value, list):
                for x in value:
                    if isinstance(x, dict):
                        self.convert_datetime(x)
        return data


class WearablesV2UserDataGetSchema(Schema):
    results = fields.List(fields.Nested(WearablesV2UserDataSchema))

class WearablesV2UserAuthUrlInputSchema(Schema):
    platform = fields.String(
        required=False,
        load_default='ios',
        validate=validate.OneOf(('ios', 'android')))


class WearablesV2BloodGlucoseCalculationOutputSchema(Schema):
    user_id = fields.Integer(required=True)
    wearable = fields.String(required=True)
    average_glucose = fields.Float(missing=None)
    standard_deviation = fields.Float(missing=None)
    glucose_management_indicator = fields.Float(missing=None)
    glucose_variability = fields.Float(missing=None)

    
class WearablesCGMPercentiles(Schema):
    count = fields.Integer()
    minute = fields.Integer()
    avg_glucose_mg_per_dL = fields.Float()
    min = fields.Float()
    max = fields.Float()
    min = fields.Float()
    percentile_5th = fields.Float()
    percentile_25th = fields.Float()
    percentile_50th = fields.Float()
    percentile_75th = fields.Float()
    percentile_95th = fields.Float()

class WearablesV2CGMPercentilesOutputSchema(Schema):
    user_id = fields.Integer(required=True)
    data = fields.Nested(WearablesCGMPercentiles(many = True))
    wearable = fields.String(required=True)
    bin_size_mins = fields.Integer()
class WearablesV2BloodPressureCalculationTimeBlockSchema(Schema):
    average_systolic = fields.Integer(default=None)
    average_diastolic = fields.Integer(default=None)
    average_pulse = fields.Integer(default=None)
    min_systolic = fields.Integer(default=None)
    max_systolic = fields.Integer(default=None)
    min_diastolic = fields.Integer(default=None)
    max_diastolic = fields.Integer(default=None)
    total_bp_readings = fields.Integer(default=0)
    total_pulse_readings = fields.Integer(default=0)

class WearablesV2BloodPressureCalculationOutputSchema(Schema):
    user_id = fields.Integer(required=True)
    wearable = fields.String(required=True)
    block_one = fields.Nested(WearablesV2BloodPressureCalculationTimeBlockSchema, default={})
    block_two = fields.Nested(WearablesV2BloodPressureCalculationTimeBlockSchema, default={})
    block_three = fields.Nested(WearablesV2BloodPressureCalculationTimeBlockSchema, default={})
    block_four = fields.Nested(WearablesV2BloodPressureCalculationTimeBlockSchema, default={})
    block_five = fields.Nested(WearablesV2BloodPressureCalculationTimeBlockSchema, default={})
    block_six = fields.Nested(WearablesV2BloodPressureCalculationTimeBlockSchema, default={})
    block_seven = fields.Nested(WearablesV2BloodPressureCalculationTimeBlockSchema, default={})
    block_eight = fields.Nested(WearablesV2BloodPressureCalculationTimeBlockSchema, default={})

class WearablesV2BloodPressureVariationCalculationOutputSchema(Schema):
    user_id = fields.Integer(required=True)
    wearable = fields.String(required=True)
    diastolic_bp_avg = fields.Float(default=None)
    systolic_bp_avg = fields.Float(default=None)
    diastolic_standard_deviation = fields.Float(default=None)
    systolic_standard_deviation = fields.Float(default=None)
    diastolic_bp_coefficient_of_variation = fields.Float(default=None)
    systolic_bp_coefficient_of_variation = fields.Float(default=None)
    
    @post_dump
    def make_object(self, data, **kwargs):
        # Round the calculations if they are not null
        data_points = [
            'diastolic_bp_avg',
            'systolic_bp_avg',
            'diastolic_standard_deviation',
            'systolic_standard_deviation',
            'diastolic_bp_coefficient_of_variation',
            'systolic_bp_coefficient_of_variation',
        ]
        for datum in data_points:
            if data.get(datum):
                data[datum] = int(round(data.get(datum), 0))

        return data
    
class WearablesV2BloodGlucoseTimeInRangesSchema(Schema):
    very_low_percentage = fields.Float(load_default=None)
    very_low_total_time = fields.String(load_default=None)
    low_percentage = fields.Float(load_default=None)
    low_total_time = fields.String(load_default=None) 
    target_range_percentage = fields.Float(load_default=None)
    target_range_total_time = fields.String(load_default=None)
    high_percentage = fields.Float(load_default=None)
    high_total_time = fields.String(load_default=None)
    very_high_percentage = fields.Float(load_default=None)
    very_high_total_time = fields.String(load_default=None)

    @post_dump
    def make_object(self, data, **kwargs):
        if data.get('very_low_total_time'):
            data['very_low_total_time'] = self.format_to_hour_min(data.get('very_low_total_time'))
        if data.get('low_total_time'):
            data['low_total_time'] = self.format_to_hour_min(data.get('low_total_time'))
        if data.get('target_range_total_time'):
            data['target_range_total_time'] = self.format_to_hour_min(data.get('target_range_total_time'))
        if data.get('high_total_time'):
            data['high_total_time'] = self.format_to_hour_min(data.get('high_total_time'))
        if data.get('very_high_total_time'):
            data['very_high_total_time'] = self.format_to_hour_min(data.get('very_high_total_time'))

        return data
    
    def format_to_hour_min(self, total_minutes):
        hours = int(float(total_minutes)) // 60
        minutes = int(float(total_minutes)) % 60

        if hours != 0:
            return f'{str(hours)} h {str(minutes)} min'
        else:
            return f'{str(minutes)} min'
        
class WearablesV2BloodGlucoseTimeInRangesOutputSchema(Schema):
    wearable = fields.String(required=True)
    user_id = fields.Integer(required=True)
    results = fields.Nested(WearablesV2BloodGlucoseTimeInRangesSchema)