from marshmallow import Schema, fields, post_load

from odyssey import ma
from odyssey.api.payment.models import PaymentMethods, PaymentStatus
from odyssey.utils.base.schemas import BaseSchema

class PaymentMethodsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PaymentMethods
        dump_only = ('created_at', 'updated_at', 'idx', 'payment_id', 'payment_type', 'number')

    token = fields.String(load_only=True, required=True)
    expiration = fields.String(load_only=True, required=True)

class PaymentStatusSchema(BaseSchema):
    class Meta:
        model = PaymentStatus