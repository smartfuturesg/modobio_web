from marshmallow import Schema, fields, post_load, validate, pre_dump, validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from odyssey import ma
from odyssey.api.dosespot.models import ( 
    DoseSpotPractitionerID,
    DoseSpotPatientID
)
from odyssey.api.user.models import User
from odyssey.utils.constants import MEDICAL_CONDITIONS
from odyssey.utils.base.schemas import BaseSchema

"""
    Schemas for the DoseSpot's API
"""

class DoseSpotPrescribeSSO(Schema):
    url = fields.String()

class DoseSpotCreatePractitionerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DoseSpotPractitionerID
        exclude = ('created_at',)
        dump_only = ('idx','user_id')
        include_fk = True

    @post_load
    def make_object(self, data, **kwargs):
        return DoseSpotPractitionerID(**data)

class DoseSpotCreatePatientSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DoseSpotPatientID
        exclude = ('created_at',)
        dump_only = ('idx','user_id')
        include_fk = True

    @post_load
    def make_object(self, data, **kwargs):
        return DoseSpotPatientID(**data)


