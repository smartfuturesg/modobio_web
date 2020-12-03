from marshmallow import Schema, fields, post_load, validate

from odyssey import ma
from odyssey.api.user.models import User, UserLogin
from odyssey.utils.constants import ACCESS_ROLES

"""
   Schemas for user accounts
"""
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('created_at', 'updated_at')

    modobio_id = fields.String(missing=None, dump_only=True)

    @post_load
    def make_object(self, data, **kwargs):
        new_user = User(**data)
        return new_user
    

class UserLoginSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserLogin

    user_id = fields.Integer()

    @post_load
    def make_object(self, data, **kwargs):
        new_user = UserLogin(**data)
        new_user.set_password(data['password'])
        return new_user


class NewClientUserSchema(Schema):
    """
    Schema for validating payloads from the creation of a new client user
    """
    firstname = fields.String()
    middlename = fields.String()
    lastname = fields.String()
    email = fields.Email(validate=validate.Length(min=0,max=50))
    phone_number = fields.String(validate=validate.Length(min=0,max=50))
    password = fields.String(validate=validate.Length(min=0,max=50), dump_only=True)
    modobio_id = fields.String(dump_only=True)
    biological_sex_male = fields.Boolean()

class UserInfoSchema(Schema):
    """
        Schema for validating payloads for the creating of a new User
    """
    firstname = fields.String()
    middlename = fields.String()
    lastname = fields.String()
    email = fields.Email(validate=validate.Length(min=0,max=50))
    phone_number = fields.String(validate=validate.Length(min=0,max=50))
    password = fields.String(description="password required when creating a staff member",
                            validate=validate.Length(min=0,max=50), 
                            required=False)
    biological_sex_male = fields.Boolean() 
    

class StaffInfoSchema(Schema):
    """
    Staff-user specific creation payload validation
    Currently just holds access_roles 
    """
    access_roles = fields.List(
                    fields.String(validate=validate.OneOf(ACCESS_ROLES)), 
                    description=f"Access roles the new user will have. Options include: {ACCESS_ROLES}"
                )
class NewUserSchema(Schema):
    """
    General purpose user creation schema
    """

    userinfo = fields.Nested(UserInfoSchema, required=True)
    staffinfo = fields.Nested(StaffInfoSchema,
                              missing={}, 
                              description="used when registering a staff member")

class UserPasswordRecoveryContactSchema(Schema):
    """contact methods for password recovery.
        currently just email but may be expanded to include sms
    """
    email = fields.Email(required=True)

class UserPasswordResetSchema(Schema):
    #TODO Validate password strength
    password = fields.String(required=True,  validate=validate.Length(min=3,max=50), description="new password to be used going forward")

class UserPasswordUpdateSchema(Schema):
    #TODO Validate password strength
    current_password = fields.String(required=True,  validate=validate.Length(min=3,max=50), description="current password")
    new_password = fields.String(required=True,  validate=validate.Length(min=3,max=50), description="new password to be used going forward")
