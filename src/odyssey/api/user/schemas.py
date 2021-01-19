from marshmallow import Schema, fields, post_load, validate

from odyssey import ma
from odyssey.api.user.models import User, UserLogin, UserSubscriptions
from odyssey.utils.constants import ACCESS_ROLES

"""
   Schemas for user accounts
"""
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('created_at', 'updated_at')
        dump_only = ('password', 'modobio_id')

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

class UserInfoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('created_at', 'updated_at')
        load_only = ('password')
        dump_only = ('is_staff', 'is_client')

    email = fields.Email(validate=validate.Length(min=0,max=50))
    phone_number = fields.String(validate=validate.Length(min=0,max=50))
    password = fields.String(description="password required when creating a staff member",
                            validate=validate.Length(min=0,max=50), 
                            required=False)

#Commented out because it felt redundant, using UserInfoSchema instead
# class NewClientUserSchema(Schema):
#    """
#    Schema for validating payloads from the creation of a new client user
#    """
#    firstname = fields.String()
#    middlename = fields.String()
#    lastname = fields.String()
#    email = fields.Email(validate=validate.Length(min=0,max=50))
#    phone_number = fields.String(validate=validate.Length(min=0,max=50))
#    password = fields.String(validate=validate.Length(min=0,max=50), load_only=True)
#    modobio_id = fields.String()
#    biological_sex_male = fields.Boolean()

    user_info = fields.Nested(UserInfoSchema, required=True)

class UserInfoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('created_at', 'updated_at', 'is_staff', 'is_client')
        dump_only = ('modobio_id', 'user_id')

    email = fields.Email(validate=validate.Length(min=0,max=50), required=True)
    phone_number = fields.String(validate=validate.Length(min=0,max=50))
    password = fields.String(validate=validate.Length(min=0,max=50), 
                            required=True)
    
class UserInfoPutSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('created_at', 'updated_at')
        dump_only = ('is_staff', 'is_client', 'modobio_id', 'user_id')

    email = fields.Email(validate=validate.Length(min=0,max=50))
    phone_number = fields.String(validate=validate.Length(min=0,max=50))

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

    user_info = fields.Nested(UserInfoSchema, required=True)
    staff_info = fields.Nested(StaffInfoSchema,
                              missing={}, 
                              description="used when registering a staff member")

class NewStaffUserSchema(UserInfoSchema):
    """
    General purpose user creation schema
    """

    user_info = fields.Nested(UserInfoSchema, required=True)
    staff_info = fields.Nested(StaffInfoSchema,
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

class UserSubscriptionsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserSubscriptions
        exclude = ('created_at', 'updated_at', 'idx')
        dump_only = ('start_date', 'end_date')

    user_id = fields.Integer()
    subscription_type = fields.String(validate=validate.OneOf(['unsubscribed', 'subscribed', 'free_trial', 'sponsored']))
    
    @post_load
    def make_object(self, data, **kwargs):
        return UserSubscriptions(**data)

class UserSubscriptionHistorySchema(Schema):

    client_subscription_history = fields.Nested(UserSubscriptionsSchema, many=True)
    staff_subscription_history = fields.Nested(UserSubscriptionsSchema, many=True)
