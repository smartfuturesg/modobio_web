import logging
logger = logging.getLogger(__name__)

from marshmallow import fields, validate
from marshmallow.decorators import post_load
from odyssey import ma

from odyssey.api.practitioner.models import PractitionerOrganizationAffiliation
from odyssey.api.lookup.schemas import LookupOrganizationsSchema

"""
    Schemas for the practitioner API
"""

class PractitionerOrganizationAffiliationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PractitionerOrganizationAffiliation
        include_fk = True
        exclude = ('created_at', 'updated_at', 'idx',)
        dump_only = ('user_id',)

    org_info = fields.Nested(LookupOrganizationsSchema(many=False), missing=[], dump_only=True)
    organization_idx = fields.Integer(required=True)

    @post_load
    def make_object(self, data, **kwargs):
        return PractitionerOrganizationAffiliation(**data)
