from marshmallow import fields, validate

from odyssey import ma


class PostOrganizationInputSchema(ma.SQLAlchemyAutoSchema):
    name = fields.String(required=True, validate=validate.Length(min=3, max=100))
    max_members = fields.Integer(required=True, validate=validate.Range(min=1, max=10000))
    max_admins = fields.Integer(required=True, validate=validate.Range(min=1, max=10000))
    owner = fields.String(required=True)
    owner_email_provided = fields.Boolean(required=True)


class PostOrganizationOutputSchema(ma.SQLAlchemyAutoSchema):
    uuid = fields.UUID()
    name = fields.String()
    max_members = fields.Integer()
    max_admins = fields.Integer()
    owner = fields.String()
