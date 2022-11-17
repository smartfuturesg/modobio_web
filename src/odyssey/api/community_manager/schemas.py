import logging

from odyssey.api.community_manager.models import CommunityManagerSubscriptionGrants
from odyssey.api.practitioner.models import PractitionerCredentials
from odyssey.api.provider.models import ProviderRoleRequests
from odyssey.api.staff.models import StaffRoles

logger = logging.getLogger(__name__)

from marshmallow import Schema, fields

from odyssey import ma

class SubscriptionGrantSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CommunityManagerSubscriptionGrants
        exclude = ('created_at', 'updated_at', 'idx', 'subscription_grantee_user_id')
        dump_only = ('user_id', )
    
    modobio_id = fields.String(dump_only = True, default=None)

class PostSubscriptionGrantSchema(Schema):

    modobio_ids = fields.List(fields.String(), missing=[])
    emails = fields.List(fields.Email(), missing=[])
    sponsor = fields.String(required=True)
    subscription_type_id = fields.Integer(required=True)


class SubscriptionGrantsAllSchema(Schema):
    subscription_grants = fields.List(fields.Nested(SubscriptionGrantSchema), missing=[])
    total_items = fields.Integer(missing=0)

class PaginationLinks(Schema):
    _next = fields.String()
    _prev = fields.String()
    
class ProviderLicensingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PractitionerCredentials
        exclude = ('idx',)

    firstname = fields.String()
    lastname = fields.String()
    modobio_id = fields.String()

class ProviderLiscensingAllSchema(Schema):
    provider_licenses = fields.List(fields.Nested(ProviderLicensingSchema), missing=[])
    total_items = fields.Integer()
    _links = fields.Nested(PaginationLinks)

class VerifyMedicalCredentialSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PractitionerCredentials
        exclude = ('country_id','role_id')
        
    user_id = fields.Integer(required=True)


class ProviderRolesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = StaffRoles
        exclude = ('idx', 'created_at', 'updated_at', 'user_id')
        dump_only = ('user_id', )
    
class ProviderRoleRequestsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProviderRoleRequests
        exclude = ('idx',)

    first_name = fields.String()
    last_name = fields.String()
    modobio_id = fields.String()
    email = fields.Email()
    current_roles = fields.Nested(ProviderRolesSchema, many=True)

class ProviderRoleRequestsAllSchema(Schema):
    provider_role_requests = fields.List(fields.Nested(ProviderRoleRequestsSchema), missing=[])
    total_items = fields.Integer()
    _links = fields.Nested(PaginationLinks)