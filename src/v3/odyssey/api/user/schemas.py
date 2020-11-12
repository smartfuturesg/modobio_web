from marshmallow import Schema, fields, post_load, validate

from odyssey import ma
from odyssey.api.user.models import User, UserLogin

"""
   Schemas for user accounts
"""
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

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

class NewUserSchema(Schema):

    firstname = fields.String()
    middlename = fields.String()
    lastname = fields.String()
    email = fields.Email(validate=validate.Length(min=0,max=50))
    phone_number = fields.String(validate=validate.Length(min=0,max=50))
    password = fields.String(validate=validate.Length(min=0,max=50))
    is_staff = fields.Boolean()
    is_client = fields.Boolean()
