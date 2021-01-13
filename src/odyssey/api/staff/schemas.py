from marshmallow import Schema, fields, post_load, validate

from odyssey import ma
from odyssey.api.user.models import User
from odyssey.api.staff.models import StaffProfile, StaffRoles, StaffRecentClients
from odyssey.utils.constants import ACCESS_ROLES

"""
    Schemas for the staff API
"""

class StaffRecentClientsSchema(Schema):
    idx = fields.Integer()
    staff_user_id = fields.Integer()
    client_user_id = fields.Integer(required=True)
    timestamp = fields.DateTime()

    @post_load
    def make_object(self, data, **kwargs):
        return StaffRecentClients(**data)

class StaffSearchItemsSchema(Schema):
    user_id = fields.Integer()
    firstname = fields.String(required=False, validate=validate.Length(min=1, max= 50), missing=None)
    lastname = fields.String(required=False, validate=validate.Length(min=1,max=50), missing=None)
    email = fields.Email(required=False, missing=None)   

class StaffProfileSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = StaffProfile

    idx = fields.Integer()
    user_id = fields.Integer()
    possible_roles = ACCESS_ROLES

    @post_load
    def make_object(self, data, **kwargs):
        return StaffProfile(**data)

class StaffRolesSchema(Schema):
    """
    Schema loads data into a StaffRoles object
    """
    
    user_id = fields.Integer()
    role = fields.String()
    # TDOD: default to false once verification process is created
    verified = fields.Boolean(default=True) 

    @post_load
    def make_object(self, data, **kwargs):
        return StaffRoles(**data)

class StaffTokenRequestSchema(Schema):
    user_id = fields.Integer()
    firstname = fields.String(required=False, validate=validate.Length(min=1, max= 50), missing=None)
    lastname = fields.String(required=False, validate=validate.Length(min=1,max=50), missing=None)
    email = fields.Email(required=False, missing=None)   
    token = fields.String()
    refresh_token = fields.String()
    access_roles = fields.List(fields.String)
    
