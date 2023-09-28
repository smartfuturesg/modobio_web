"""Schemas for the wearables API"""
import logging

logger = logging.getLogger(__name__)

from datetime import datetime

from marshmallow import EXCLUDE, Schema, fields, post_dump, pre_dump, validate

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
        exclude = ("idx", "user_id", "created_at", "updated_at")


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
        exclude = ("idx", "user_id", "created_at", "updated_at")


class WearablesFreeStyleActivateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WearablesFreeStyle
        load_instance = True
        fields = ("activation_timestamp",)


##############################
#
# V2 of the Wearables schemas.
#
##############################

import terra.api.api_responses
from marshmallow_dataclass import class_schema
from terra.models.user import User
from terra.models.v2.activity import Activity
from terra.models.v2.athlete import Athlete
from terra.models.v2.body import Body
from terra.models.v2.daily import Daily
from terra.models.v2.menstruation import Menstruation
from terra.models.v2.nutrition import Nutrition
from terra.models.v2.sleep import Sleep


class RoundedFloat(fields.Float):
    def __init__(self, decimals=2, **kwargs):
        self.decimals = decimals
        super().__init__(**kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return round(value, self.decimals)


class WearablesV2BaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        load_only = ("status", "user_id")


# Automatically convert all Terra classes to marshmallow schemas.
# Terra defines all responses as dataclasses.dataclass. Use the
# module marshmallow_dataclass to convert those directly to
# marshmallow schemas.

# API response classes
for response_class_name in terra.api.api_responses.__all__:
    response_class = getattr(terra.api.api_responses, response_class_name)
    response_schema = class_schema(response_class, WearablesV2BaseSchema)
    globals()[f"WearablesV2{response_class_name}Schema"] = response_schema

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
WearablesV2UserAuthUrlSchema = WearablesV2UserAuthUrlSchema.from_dict(
    {"token": fields.String(default=None)}
)


# Additional schemas
class WearablesV2UserGetSchema(Schema):
    wearables = fields.List(fields.String(), dump_default=[])


class WearablesV2ProvidersGetSchema(Schema):
    providers = fields.Dict(keys=fields.String(), values=fields.String())
    sdk_providers = fields.Dict(keys=fields.String(), values=fields.String())


class WearablesV2UserDataSchema(Schema):
    user_id = fields.Integer()
    wearable = fields.String()
    timestamp = fields.DateTime(format="%Y-%m-%dT%H:%M:%S%z")
    data = fields.Dict()

    @pre_dump
    def handle_datetime_fields(self, data, **kwargs):
        """
        Converts datetime objects to the string representation in the 'data'
        part of the mongo documents in order to serialize the object correctly
        """
        result = self.convert_datetime(data["data"])
        data["data"] = result
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
        load_default="ios",
        validate=validate.OneOf(("ios", "android")),
    )


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
    data = fields.Nested(WearablesCGMPercentiles(many=True))
    wearable = fields.String(required=True)
    bin_size_mins = fields.Integer()
    start_time = fields.DateTime()
    end_time = fields.DateTime()


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
    block_one = fields.Nested(
        WearablesV2BloodPressureCalculationTimeBlockSchema, default={}
    )
    block_two = fields.Nested(
        WearablesV2BloodPressureCalculationTimeBlockSchema, default={}
    )
    block_three = fields.Nested(
        WearablesV2BloodPressureCalculationTimeBlockSchema, default={}
    )
    block_four = fields.Nested(
        WearablesV2BloodPressureCalculationTimeBlockSchema, default={}
    )
    block_five = fields.Nested(
        WearablesV2BloodPressureCalculationTimeBlockSchema, default={}
    )
    block_six = fields.Nested(
        WearablesV2BloodPressureCalculationTimeBlockSchema, default={}
    )
    block_seven = fields.Nested(
        WearablesV2BloodPressureCalculationTimeBlockSchema, default={}
    )
    block_eight = fields.Nested(
        WearablesV2BloodPressureCalculationTimeBlockSchema, default={}
    )


class WearablesV2BloodPressureCalculationClassificationSchema(Schema):
    normal = fields.Integer(default=0)
    elevated = fields.Integer(default=0)
    hypertension_stage_1 = fields.Integer(default=0)
    hypertension_stage_2 = fields.Integer(default=0)
    hypertensive_crisis = fields.Integer(default=0)
    normal_percentage = fields.Integer(default=0)
    elevated_percentage = fields.Integer(default=0)
    hypertension_stage_1_percentage = fields.Integer(default=0)
    hypertension_stage_2_percentage = fields.Integer(default=0)
    hypertensive_crisis_percentage = fields.Integer(default=0)


class WearablesV2BloodPressureMonitoringStatisticsGeneralInfoSchema(Schema):
    average_systolic = fields.Integer(default=None)
    average_diastolic = fields.Integer(default=None)
    min_systolic = fields.Integer(default=None)
    max_systolic = fields.Integer(default=None)
    min_diastolic = fields.Integer(default=None)
    max_diastolic = fields.Integer(default=None)
    total_bp_readings = fields.Integer(default=0)
    total_pulse_readings = fields.Integer(default=0)
    average_pulse = fields.Integer(default=None)
    average_readings_per_day = fields.Float(default=None)
    min_pulse = fields.Integer(default=None)
    max_pulse = fields.Integer(default=None)


class WearablesV2BloodPressureMonitoringStatisticsTimeBlockSchema(Schema):
    start_date = fields.DateTime()
    end_date = fields.DateTime()
    general_data = fields.Nested(
        WearablesV2BloodPressureMonitoringStatisticsGeneralInfoSchema,
        default={},
    )
    classification_data = fields.Nested(
        WearablesV2BloodPressureCalculationClassificationSchema, default={}
    )


class WearablesV2BloodPressureMonitoringStatisticsOutputSchema(Schema):
    user_id = fields.Integer(required=True)
    wearable = fields.String(required=True)
    current_block = fields.Nested(
        WearablesV2BloodPressureMonitoringStatisticsTimeBlockSchema, default={}
    )
    prev_block = fields.Nested(
        WearablesV2BloodPressureMonitoringStatisticsTimeBlockSchema, default={}
    )


class WearablesV2BloodPressureVariationCalculationOutputSchema(Schema):
    user_id = fields.Integer(required=True)
    wearable = fields.String(required=True)
    diastolic_bp_avg = fields.Integer(default=None)
    systolic_bp_avg = fields.Integer(default=None)
    diastolic_standard_deviation = fields.Integer(default=None)
    systolic_standard_deviation = fields.Integer(default=None)
    diastolic_bp_coefficient_of_variation = fields.Integer(default=None)
    systolic_bp_coefficient_of_variation = fields.Integer(default=None)
    pulse_avg = fields.Integer(default=None)
    pulse_standard_deviation = fields.Integer(default=None)
    pulse_coefficient_of_variation = fields.Integer(default=None)


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
        if data.get("very_low_total_time"):
            data["very_low_total_time"] = self.format_to_hour_min(
                data.get("very_low_total_time")
            )
        if data.get("low_total_time"):
            data["low_total_time"] = self.format_to_hour_min(data.get("low_total_time"))
        if data.get("target_range_total_time"):
            data["target_range_total_time"] = self.format_to_hour_min(
                data.get("target_range_total_time")
            )
        if data.get("high_total_time"):
            data["high_total_time"] = self.format_to_hour_min(
                data.get("high_total_time")
            )
        if data.get("very_high_total_time"):
            data["very_high_total_time"] = self.format_to_hour_min(
                data.get("very_high_total_time")
            )

        return data

    def format_to_hour_min(self, total_minutes):
        hours = int(float(total_minutes)) // 60
        minutes = int(float(total_minutes)) % 60

        if hours != 0:
            return f"{str(hours)} h {str(minutes)} min"
        else:
            return f"{str(minutes)} min"


class WearablesV2BloodGlucoseTimeInRangesOutputSchema(Schema):
    wearable = fields.String(required=True)
    user_id = fields.Integer(required=True)
    results = fields.Nested(WearablesV2BloodGlucoseTimeInRangesSchema)


class WearablesV2BloodPressureDailyAvgNestedSchema(Schema):
    date = fields.Date(required=True)
    systolic_bp_avg = fields.Integer(required=True)
    diastolic_bp_avg = fields.Integer(required=True)
    bp_readings_count = fields.Integer(required=True)
    hr_bpm_avg = fields.Integer(required=True)
    hr_readings_count = fields.Integer(required=True)


class WearablesV2BloodPressureDailyAvgOutputSchema(Schema):
    wearable = fields.String(required=True)
    items = fields.List(fields.Nested(WearablesV2BloodPressureDailyAvgNestedSchema))
    total_items = fields.Integer(required=True)


class DailyMetricsSchema(Schema):
    total_duration_asleep = fields.Int()
    total_duration_REM = fields.Int()
    total_duration_light_sleep = fields.Int()
    total_duration_deep_sleep = fields.Int()
    total_duration_in_bed = fields.Int()
    resting_hr = fields.Int()
    total_steps = fields.Int()
    total_distance_feet = fields.Float()
    total_calories = fields.Int()
    active_calories = fields.Int()
    date = fields.Date()


class WearablesV2DashboardOutputSchema(Schema):
    daily_metrics = fields.Nested(DailyMetricsSchema, many=True)
    total_days = fields.Int(load_default=0)
    avg_resting_hr = fields.Float()
    avg_steps = fields.Float()
    avg_distance_feet = fields.Float()
    avg_sleep_duration = fields.Float()
    avg_in_bed_duration = fields.Float()
    avg_calories = fields.Float()
    avg_active_calories = fields.Float()


class WearablesV2RawBPSchema(Schema):
    timestamp = fields.DateTime()
    systolic_bp = fields.Integer()
    diastolic_bp = fields.Integer()
    bpm = fields.Integer()
    wearable = fields.String()


class WearablesV2RawBPOutputSchema(Schema):
    items = fields.List(fields.Nested(WearablesV2RawBPSchema))
    total_items = fields.Integer(required=True)
