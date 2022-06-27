import logging
logger = logging.getLogger(__name__)

from marshmallow import Schema, fields, validate

from odyssey import ma
from odyssey.api.user.models import User, UserLogin


# Don't use user.schemas.User(Login)Schema here,
# need a different set of attributes.
class CSUserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = (
            'created_at',
            'updated_at',
            'staff_profile',
            'client_info',
            'is_internal')


class CSUserLoginSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserLogin
        exclude = (
            'created_at',
            'updated_at',
            'idx',
            'user_id',
            'password',
            'last_login',
            'refresh_token')


class CSAccountBlockSchema(Schema):
    staff = fields.Boolean(required=True)
    reason = fields.String(required=True, validate=validate.Length(max=500))


class CSAccountUnblockSchema(Schema):
    staff = fields.Boolean(required=True)

