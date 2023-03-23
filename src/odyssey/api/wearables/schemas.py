""" Schemas for the wearables API """
import logging
logger = logging.getLogger(__name__)

from marshmallow import Schema, fields, EXCLUDE, post_dump, validate

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


class WearablesV2UserAuthUrlInputSchema(Schema):
    platform = fields.String(
        required=False,
        load_default='ios',
        validate=validate.OneOf(('ios', 'android')))


class WearablesV2BloodGlucoseCalculationOutputSchema(Schema):
    user_id = fields.Integer(required=True)
    wearable = fields.String(required=True)
    average_glucose = fields.Integer(missing=None)
    standard_deviation = fields.Float(missing=None)
    glucose_management_indicator = fields.Float(missing=None)
    glucose_variability = fields.Float(missing=None)

    @post_dump
    def make_object(self, in_data, **kwargs):
        # Round the calculations if they are not null
        if in_data.get('standard_deviation'):
            in_data['standard_deviation'] = round(in_data.get('standard_deviation'), 1)
        if in_data.get('glucose_management_indicator'):
            in_data['glucose_management_indicator'] = round(in_data.get('glucose_management_indicator'), 1)
        if in_data.get('glucose_variability'):
            in_data['glucose_variability'] = round(in_data.get('glucose_variability'), 1)

        return in_data
    
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

    
