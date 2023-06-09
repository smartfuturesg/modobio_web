from marshmallow import fields, validate

from odyssey import ma


class PostOrganizationInputSchema(ma.SQLAlchemyAutoSchema):
    name = fields.String(required=True, validate=validate.Length(min=3, max=100))
    max_members = fields.Integer(required=True, validate=validate.Range(min=1, max=10000))
    max_admins = fields.Integer(required=True, validate=validate.Range(min=1, max=10000))
    owner = fields.Integer(required=True)


class PostOrganizationOutputSchema(ma.SQLAlchemyAutoSchema):
    organization_id = fields.Integer()
    name = fields.String()
    max_members = fields.Integer()
    max_admins = fields.Integer()
    owner = fields.Integer()
