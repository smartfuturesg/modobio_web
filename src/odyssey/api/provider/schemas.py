import logging
from odyssey.api.provider.models import ProviderRoleRequests

from odyssey.api.staff.models import StaffRoles
logger = logging.getLogger(__name__)

from marshmallow import fields, validate, Schema
from marshmallow.decorators import post_load, pre_load
from sqlalchemy import select
from odyssey import ma,db

from odyssey.api.practitioner.models import PractitionerOrganizationAffiliation, PractitionerCredentials
from odyssey.api.lookup.schemas import LookupOrganizationsSchema, LookupRolesSchema
from odyssey.utils.constants import CREDENTIAL_TYPE, USSTATES_2, CREDENTIAL_STATUS, CREDENTIAL_ROLES

"""
    Schemas for the practitioner API
"""

class ProviderConsultationRateSchema(Schema):
    role = fields.String()
    rate = fields.String()

class ProviderConsultationRateInputSchema(Schema):
    items = fields.Nested(ProviderConsultationRateSchema(many=True),missing = [])

class ProviderOrganizationAffiliationSchema(ma.SQLAlchemyAutoSchema):
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

class ProviderCredentialsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PractitionerCredentials
        exclude = ('created_at','updated_at')
        dump_only = ('timestamp','user_id', 'role_id')
        include_fk = True
    
    idx = fields.Integer(required=False, dump_only=True)
    state = fields.String(validate=validate.OneOf(USSTATES_2))
    status = fields.String(validate=validate.OneOf(CREDENTIAL_STATUS) ,missing='Pending Verification', dump_only=True)
    credential_type = fields.String(validate=validate.OneOf(CREDENTIAL_TYPE['medical_doctor']))
    staff_role = fields.String(validate=validate.OneOf(CREDENTIAL_ROLES), required=True)
    expiration_date = fields.Date(required=False)

    @post_load
    def make_object(self, data, **kwargs):
        role = data.pop("staff_role")
        return (role, PractitionerCredentials(**data))

class ProviderCredentialsInputSchema(Schema):
    items = fields.Nested(ProviderCredentialsSchema(many=True))

class ProviderDeleteCredentialsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PractitionerCredentials
        only = ('idx')


class ProviderRoleRequestsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProviderRoleRequests
        exclude = ('created_at','updated_at')
        dump_only = ('user_id', 'role_id', 'idx')
        include_fk = True

    role_info= fields.Nested(LookupRolesSchema(many=False), missing=[], dump_only=True)

class ProviderRoleRequestsAllSchema(Schema):
    items = fields.Nested(ProviderRoleRequestsSchema(many=True))
    total_items = fields.Integer()
    

    

    

    