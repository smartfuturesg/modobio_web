import logging

logger = logging.getLogger(__name__)

from marshmallow import Schema, fields, validate

from odyssey import ma
from odyssey.api.user.models import User, UserLogin


class SubscriptionGrantSchema(Schema):
    modobio_ids = fields.List(fields.String(), missing=[])
    emails = fields.List(fields.Email(), missing=[])
    sponsor = fields.String(required=True)
    subscription_type_id = fields.Integer(required=True)
