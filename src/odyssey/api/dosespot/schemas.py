from marshmallow import Schema, fields, post_load, validate, pre_dump, validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from odyssey import ma
from odyssey.api.dosespot.models import ( 
    DoseSpotUserID
)
from odyssey.api.user.models import User
from odyssey.utils.constants import MEDICAL_CONDITIONS
from odyssey.utils.base.schemas import BaseSchema

"""
    Schemas for the DoseSpot's API
"""

class DoseSpotCreateUserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DoseSpotUserID
        exclude = ('created_at',)
        dump_only = ('timestamp','idx', 'reporter_id', 'user_id')
        include_fk = True
        
    timestamp = fields.DateTime()
    systolic = fields.Float(metadata={'description':'units mmHg'},required=True)
    diastolic = fields.Float(metadata={'description':'units mmHg'},required=True)
    datetime_taken = fields.String(metadata={'description':'Date and time the blood pressure was taken'}, required=True)
    reporter_firstname = fields.String(metadata={'description': 'first name of reporting physician'}, dump_only=True)
    reporter_lastname = fields.String(metadata={'description': 'last name of reporting physician'}, dump_only=True)
    

    @post_load
    def make_object(self, data, **kwargs):
        return DoseSpotUserID(**data)