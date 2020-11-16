from marshmallow import Schema, fields, post_load, validate

from odyssey import ma
from odyssey.api.user.models import User
from odyssey.api.staff.models import StaffProfile, StaffRoles
from odyssey.utils.constants import ACCESS_ROLES

"""
    Schemas for the staff API
"""

class StaffPasswordRecoveryContactSchema(Schema):
    """contact methods for password recovery.
        currently just email but may be expanded to include sms
    """
    email = fields.Email(required=True)

class StaffPasswordResetSchema(Schema):
    #TODO Validate password strength
    password = fields.String(required=True,  validate=validate.Length(min=3,max=50), description="new password to be used going forward")

class StaffPasswordUpdateSchema(Schema):
    #TODO Validate password strength
    current_password = fields.String(required=True,  validate=validate.Length(min=3,max=50), description="current password")
    new_password = fields.String(required=True,  validate=validate.Length(min=3,max=50), description="new password to be used going forward")

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
