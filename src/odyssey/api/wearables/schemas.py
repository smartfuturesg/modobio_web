""" Schemas for the wearables API """
import logging
logger = logging.getLogger(__name__)

from marshmallow import Schema, fields

from odyssey import ma
from odyssey.api.user.models import User
from odyssey.api.wearables.models import Wearables, WearablesFreeStyle


#######################################################################################
#
# V1 of the Wearables tables.
#
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

#######################################################################################
#
# V2 of the Wearables schemas.
#

import marshmallow_dataclass

from terra.models.v2.activity import Activity
from terra.models.v2.athlete import Athlete
from terra.models.v2.body import Body
from terra.models.v2.daily import Daily
from terra.models.v2.menstruation import Menstruation
from terra.models.v2.nutrition import Nutrition
from terra.models.v2.sleep import Sleep
from terra.models.user import User

WearablesTerraActivitySchema = marshmallow_dataclass.class_schema(Activity)
WearablesTerraAthleteSchema = marshmallow_dataclass.class_schema(Athlete)
WearablesTerraBodySchema = marshmallow_dataclass.class_schema(Body)
WearablesTerraDailySchema = marshmallow_dataclass.class_schema(Daily)
WearablesTerraMenstruationSchema = marshmallow_dataclass.class_schema(Menstruation)
WearablesTerraNutritionSchema = marshmallow_dataclass.class_schema(Nutrition)
WearablesTerraSleepSchema = marshmallow_dataclass.class_schema(Sleep)
WearablesTerraUserSchema = marshmallow_dataclass.class_schema(User)

class WearablesV2RegisterSchema(Schema):
    auth_success_redirect_url = fields.Url(default='')
    auth_failure_redirect_url = fields.Url(default='')
