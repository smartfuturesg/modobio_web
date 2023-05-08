import logging

from odyssey.api.provider.models import ProviderRoleRequests
from odyssey.api.staff.models import StaffRoles

logger = logging.getLogger(__name__)

from marshmallow import Schema, fields, validate
from marshmallow.decorators import post_load, pre_load
from sqlalchemy import select

from odyssey import db, ma
from odyssey.api.lookup.schemas import (LookupOrganizationsSchema, LookupRolesSchema)
from odyssey.api.practitioner.models import PractitionerOrganizationAffiliation
from odyssey.api.provider.models import ProviderCredentials
from odyssey.utils.constants import (
    CREDENTIAL_ROLES, CREDENTIAL_STATUS, CREDENTIAL_TYPES, USSTATES_2
)
"""
    Schemas for the practitioner API
"""


class ProviderConsultationRateSchema(Schema):
    role = fields.String()
    rate = fields.String()


class ProviderConsultationRateInputSchema(Schema):
    items = fields.Nested(ProviderConsultationRateSchema(many=True), missing=[])


class ProviderOrganizationAffiliationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PractitionerOrganizationAffiliation
        include_fk = True
        exclude = (
            'created_at',
            'updated_at',
            'idx',
        )
        dump_only = ('user_id', )

    org_info = fields.Nested(LookupOrganizationsSchema(many=False), missing=[], dump_only=True)
    organization_idx = fields.Integer(required=True)
    affiliate_user_id = fields.String()

    @post_load
    def make_object(self, data, **kwargs):
        return PractitionerOrganizationAffiliation(**data)


class ProviderCredentialsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProviderCredentials
        exclude = ('created_at', 'updated_at')
        dump_only = ('timestamp', 'user_id', 'role_id', 'role_request_id')
        include_fk = True

    idx = fields.Integer(required=False, dump_only=True)
    state = fields.String(validate=validate.OneOf(USSTATES_2))
    status = fields.String(
        validate=validate.OneOf(CREDENTIAL_STATUS),
        missing='Pending Verification',
        dump_only=True,
    )
    credential_type = fields.String(validate=validate.OneOf(CREDENTIAL_TYPES))
    staff_role = fields.String(validate=validate.OneOf(CREDENTIAL_ROLES), required=True)
    expiration_date = fields.Date(required=False)

    @post_load
    def make_object(self, data, **kwargs):
        role = data.pop('staff_role')
        return (role, ProviderCredentials(**data))


class ProviderCredentialsInputSchema(Schema):
    items = fields.Nested(ProviderCredentialsSchema(many=True))


class ProviderDeleteCredentialsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProviderCredentials
        only = 'idx'


class ProviderRoleRequestsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProviderRoleRequests
        exclude = ('created_at', 'updated_at')
        dump_only = ('user_id', 'role_id', 'idx')
        include_fk = True

    role_info = fields.Nested(LookupRolesSchema(many=False), missing=[], dump_only=True)


class ProviderRoleRequestsAllSchema(Schema):
    items = fields.Nested(ProviderRoleRequestsSchema(many=True))
    total_items = fields.Integer()
