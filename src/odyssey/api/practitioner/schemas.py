import logging
logger = logging.getLogger(__name__)

from marshmallow import fields, validate, Schema
from marshmallow.decorators import post_load
from sqlalchemy import select
from odyssey import ma,db

from odyssey.api.practitioner.models import PractitionerOrganizationAffiliation
from odyssey.api.lookup.models import LookupCurrencies
from odyssey.api.lookup.schemas import LookupOrganizationsSchema

"""
    Schemas for the practitioner API
"""

class PractitionerConsultationRateSchema(Schema):
    role = fields.String()
    rate = fields.String()

class PractitionerConsultationRateInputSchema(Schema):
    items = fields.Nested(PractitionerConsultationRateSchema(many=True),missing = [])

class PractitionerOrganizationAffiliationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PractitionerOrganizationAffiliation
        include_fk = True
        exclude = ('created_at', 'updated_at', 'idx',)
        dump_only = ('user_id',)

    org_info = fields.Nested(LookupOrganizationsSchema(many=False), missing=[], dump_only=True)
    organization_idx = fields.Integer(required=True)
    affiliate_user_id = fields.String()
    
    @post_load
    def make_object(self, data, **kwargs):
        return PractitionerOrganizationAffiliation(**data)
