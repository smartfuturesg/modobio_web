""" Schemas for user accounts. """

import logging
logger = logging.getLogger(__name__)

from marshmallow import Schema, fields, post_load, validate
from sqlalchemy.orm import load_only

from odyssey import ma
from odyssey.api.staff.schemas import StaffRolesSchema
from odyssey.api.user.models import User, UserLogin, UserSubscriptions, UserPendingEmailVerifications, UserLegalDocs
from odyssey.utils.constants import ACCESS_ROLES


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('created_at', 'updated_at')
        dump_only = ('password', 'modobio_id', 'email_verified')

    @post_load
    def make_object(self, data, **kwargs):
        new_user = User(**data)
        return new_user


class UserLoginSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserLogin
        exclude = (
            'staff_account_blocked',
            'staff_account_blocked_reason',
            'client_account_blocked',
            'client_account_blocked_reason')

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
        dump_only = ('modobio_id', 'user_id', 'is_internal','is_staff', 'is_client', 'deleted', 'email_verified')

    email = fields.Email(validate=validate.Length(min=0,max=50), required=True)
    phone_number = fields.String(validate=validate.Length(min=0,max=50))
    password = fields.String(metadata={'description': 'password required'},
                            validate=validate.Length(min=0,max=50), 
                            load_only=True, required=True)


class UserInfoPutSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('created_at', 'updated_at')
        dump_only = ('is_staff', 'is_client', 'modobio_id', 'user_id', 'email_verified')

    email = fields.Email(validate=validate.Length(min=0,max=50))
    phone_number = fields.String(validate=validate.Length(min=0,max=50))


class StaffInfoSchema(Schema):
    """
    Staff-user specific creation payload validation
    Currently just holds access_roles
    """
    access_roles = fields.List(
                    fields.String(validate=validate.OneOf(ACCESS_ROLES)), 
                    metadata={'description': f'Access roles the new user will have. Options include: {ACCESS_ROLES}'}
                )

    access_roles_v2 = fields.Nested(
                    StaffRolesSchema(many=True),
                    metadata={'description': f'v2 of this field now returns the internal id for the role. \
                        Access roles the new user will have. Options include: {ACCESS_ROLES}'})

class NewClientUserSchema(Schema):
    """
    Schema returned when a new client has been created,
    it includes token and refresh_token to allow login immediately after account creation
    """
    user_info = fields.Nested(UserInfoSchema, required=True)
    token = fields.String()
    refresh_token = fields.String()
    email_verification_code = fields.String()

class NewStaffUserSchema(Schema):
    """
    General purpose user creation schema
    """
    email_verification_code = fields.String()
    user_info = fields.Nested(UserInfoSchema, required=True)
    staff_info = fields.Nested(StaffInfoSchema,
                              missing={}, 
                              metadata={'description': 'used when registering a staff member'})

class UserPasswordRecoveryContactSchema(Schema):
    """contact methods for password recovery.
        currently just email but may be expanded to include sms
    """
    email = fields.Email(required=True, load_only=True)
    captcha_key = fields.String(load_only=True)
    success = fields.Boolean(dump_only=True)
    challenge_ts = fields.String(dump_only=True)
    hostname = fields.String(dump_only=True)
    error_codes = fields.List(fields.String(), dump_only=True)
    token = fields.String(dump_only=True)
    password_reset_url = fields.String(dump_only=True)

class UserPasswordResetSchema(Schema):
    #TODO Validate password strength
    password = fields.String(required=True,  validate=validate.Length(min=3,max=50), metadata={'description': 'new password to be used going forward'})

class UserPasswordUpdateSchema(Schema):
    #TODO Validate password strength
    current_password = fields.String(required=True,  validate=validate.Length(min=3,max=50), metadata={'description': 'current password'})
    new_password = fields.String(required=True,  validate=validate.Length(min=3,max=50), metadata={'description': 'new password to be used going forward'})

class UserSubscriptionTypeSchema(Schema):

    name = fields.String()
    description = fields.String()
    cost = fields.Float()
    frequency = fields.String()
    

class UserSubscriptionsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserSubscriptions
        exclude = ('created_at', 'updated_at', 'idx')
        dump_only = ('end_date', 'user_id', )
        load_only = ('apple_original_transaction_id',)

    subscription_type_id = fields.Integer(required=False, validate=validate.OneOf([2,3]))
    subscription_status = fields.String(validate=validate.OneOf(['unsubscribed', 'subscribed', 'free trial', 'sponsored']))
    expire_date = fields.DateTime(metadata={'(UTC) description': 'date this subscription purchase ends. Overall subscription may persist if it is renewed.'})
    auto_renew_status = fields.Boolean(dump_only = True, metadata={'description': 'If True the subscription is set to be renewed automatically.'})
    apple_original_transaction_id = fields.String(load_only=True, missing=None)
    subscription_type_information = fields.Nested(UserSubscriptionTypeSchema, dump_only=True)
    sponsorship_id = fields.Integer(load_only=True)
    
    @post_load
    def make_object(self, data, **kwargs):
        return UserSubscriptions(**data)

class UserSubscriptionHistorySchema(Schema):

    client_subscription_history = fields.Nested(UserSubscriptionsSchema, many=True)
    staff_subscription_history = fields.Nested(UserSubscriptionsSchema, many=True)

class UserClinicalCareTeamSchema(Schema):

    client_user_id = fields.Integer()
    client_name = fields.String()
    client_email = fields.String()

class UserLegalDocsSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = UserLegalDocs
        exclude = ('created_at', 'updated_at', 'idx')

    doc_id = fields.Integer()
    doc_name = fields.String(dump_only=True)
    doc_version = fields.Integer(dump_only=True)

    @post_load
    def make_object(self, data, **kwargs):
        return UserLegalDocs(**data)