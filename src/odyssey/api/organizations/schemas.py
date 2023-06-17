from marshmallow import Schema, fields, validate

from odyssey import ma
from odyssey.api.organizations.models import Organizations


class OrganizationsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Organizations
        exclude = ('created_at', 'updated_at')
        load_instance = True

    name = fields.String(required=True, validate=validate.Length(min=3, max=100))
    max_members = fields.Integer(required=True, validate=validate.Range(min=1, max=10000))
    max_admins = fields.Integer(required=True, validate=validate.Range(min=1, max=10000))
    owner = fields.Integer(required=True)
    organization_uuid = fields.UUID(dump_only=True)


class OrganizationMembersPostInputSchema(Schema):
    organization_uuid = fields.UUID(required=True)
    members = fields.List(fields.Integer(), required=True)
    # Using AutoSchema, nesting here is overly complex and requires far more than two lines
    # All we need a list of ints and a uuid, all necessary validation is done in the route gracefully


class OrganizationMembersPostOutputSchema(Schema):
    organization_uuid = fields.UUID(required=True)
    added_members = fields.List(fields.Integer(), required=True)
    invalid_members = fields.List(fields.Integer(), required=True)
    prior_members = fields.List(fields.Integer(), required=True)
