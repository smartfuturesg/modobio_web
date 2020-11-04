from datetime import datetime
from marshmallow import Schema, fields, post_load, ValidationError, validates, validate
from marshmallow import post_load

from odyssey import ma
from odyssey.misc.models import RegisteredFacilities
from odyssey.staff.models import Staff
from odyssey.wearables.models import Wearables
from odyssey.constants import STAFF_ROLES

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
    staffid = fields.Integer()
    firstname = fields.String(required=False, validate=validate.Length(min=1, max= 50), missing=None)
    lastname = fields.String(required=False, validate=validate.Length(min=1,max=50), missing=None)
    email = fields.Email(required=False, missing=None)

class StaffSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Staff

    possible_roles = STAFF_ROLES

    token = fields.String(dump_only=True)
    token_expiration = fields.DateTime(dump_only=True)
    password = fields.String(required=True, load_only=True)
    email = fields.Email(required=True)
    access_roles = fields.List(fields.String,
                description=" The access role for this staff member options: \
                ['stfappadmin' (staff application admin), 'clntsvc' (client services), 'physthera' (physiotherapist), 'datasci' (data scientist), 'doctor' (doctor), 'docext' (external doctor), 'phystrain' (physical trainer),\
                 'nutrition' (nutritionist)]",
                required=True)
    is_system_admin = fields.Boolean(dump_only=True, missing=False)
    is_admin = fields.Boolean(dump_only=True, missing=False)
    staffid = fields.Integer(dump_only=True)

    @validates('access_roles')
    def valid_access_roles(self,value):
        for role in value:
            if role not in self.possible_roles:
                raise ValidationError(f'{role} is not a valid access role. Use one of the following {self.possible_roles}')
            
    @post_load
    def make_object(self, data, **kwargs):
        new_staff = Staff(**data)
        new_staff.set_password(data['password'])
        return new_staff

class RegisteredFacilitiesSchema(Schema):
    facility_id = fields.Integer(required=False)
    facility_name = fields.String(required=True)
    facility_address = fields.String(required=True)
    modobio_facility = fields.Boolean(required=True)

    @post_load
    def make_object(self, data, **kwargs):
        return RegisteredFacilities(**data)

class ClientSummarySchema(Schema):

    firstname = fields.String()
    middlename = fields.String()
    lastname = fields.String()
    dob = fields.Date()
    clientid = fields.Integer()
    membersince = fields.Date()
    facilities = fields.Nested(RegisteredFacilitiesSchema(many=True))