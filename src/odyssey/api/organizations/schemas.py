from marshmallow import fields, validate

from odyssey import ma
from odyssey.api.organizations.models import Organizations


class OrganizationsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Organizations
        dump_only = ('organization_uuid', )
        load_instance = True

    name = fields.String(required=True, validate=validate.Length(min=3, max=100))
    max_members = fields.Integer(required=True, validate=validate.Range(min=1, max=10000))
    max_admins = fields.Integer(required=True, validate=validate.Range(min=1, max=10000))
    owner = fields.Integer(required=True)
