from marshmallow import Schema, fields, post_load

from odyssey import ma
from odyssey.api.dosespot.models import ( 
    DoseSpotPractitionerID,
    DoseSpotPatientID,
    DoseSpotProxyID
)
from odyssey.utils.base.schemas import BaseSchema

"""
    Schemas for the DoseSpot's API
"""

class DoseSpotEnrollmentGET(Schema):
    status = fields.String()

class DoseSpotEnrollmentSchema(Schema):
    status = fields.String()

class DoseSpotPrescribeSSO(Schema):
    url = fields.String()

class DoseSpotPharmacySelect(Schema):
    pharmacy_id = fields.Integer()

class DoseSpotPharmacyNestedSelect(Schema):
    items = fields.Nested(DoseSpotPharmacySelect(many=True))

class DoseSpotCreateProxyUserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DoseSpotProxyID
        exclude = ('created_at',)
        dump_only = ('idx',)
    @post_load
    def make_object(self,data,**kwargs):
        return DoseSpotProxyID(**data)
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


