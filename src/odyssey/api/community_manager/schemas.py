import logging

from odyssey.api.community_manager.models import CommunityManagerSubscriptionGrants

logger = logging.getLogger(__name__)

from marshmallow import Schema, fields, validate

from odyssey import ma
from odyssey.api.user.models import User, UserLogin



class SubscriptionGrantSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CommunityManagerSubscriptionGrants
        exclude = ('created_at', 'updated_at', 'idx', 'subscription_grantee_user_id')
        dump_only = ('user_id', )
    
    modobio_id = fields.String(dump_only = True, default=None)

class PostSubscriptionGrantSchema(Schema):

    modobio_ids = fields.List(fields.String(), missing=[])
    emails = fields.List(fields.Email(), missing=[])
    sponsor = fields.String(required=True)
    subscription_type_id = fields.Integer(required=True)


class SubscriptionGrantsAllSchema(Schema):
    subscription_grants = fields.List(fields.Nested(SubscriptionGrantSchema), missing=[])
    total_items = fields.Integer(missing=0)