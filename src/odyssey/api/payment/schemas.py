import logging
logger = logging.getLogger(__name__)

from marshmallow import Schema, fields, post_load, validate

from odyssey import ma
from odyssey.api.payment.models import PaymentMethods, PaymentStatus, PaymentRefunds, PaymentHistory
from odyssey.utils.base.schemas import BaseSchema

class PaymentMethodsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PaymentMethods
        dump_only = ('idx', 'payment_id', 'payment_type', 'number')
        exclude = ('created_at', 'updated_at')

    token = fields.String(load_only=True, required=True)
    expiration = fields.String(required=True)
    cardholder_name = fields.String(required=True)

class PaymentStatusSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PaymentStatus
        dump_only = ('created_at',)
        exclude = ('updated_at','idx',)

    request_amount = fields.Float()
    user_id = fields.Integer(required=True)

    @post_load
    def make_object(self, data, **kwargs):
        return PaymentStatus(**data)

class PaymentStatusOutputSchema(Schema):

    payment_statuses = fields.Nested(PaymentStatusSchema(many=True))

class PaymentHistorySchema(BaseSchema):
    class Meta:
        model = PaymentHistory
        exclude = ('created_at', 'updated_at' )


    transaction_amount = fields.String()
    transaction_descriptor = fields.String()
    transaction_date = fields.DateTime()
    transaction_updated = fields.DateTime()
    currency = fields.String()
    payment_method = fields.Nested(PaymentMethodsSchema)

    @post_load
    def make_object(self, data, **kwargs):
        return PaymentHistory(**data)

class TransactionHistorySchema(Schema):
    items = fields.Nested(PaymentHistorySchema(many=True))
    total_items = fields.Integer()


class PaymentRefundsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PaymentRefunds
        exclude = ('created_at', 'updated_at', 'idx')

    payment_id = fields.Integer(required=True)
    refund_amount = fields.String()
    refund_reason = fields.String(validate=validate.Length(min=21))
    
    @post_load
    def make_object(self, data, **kwargs):
        return PaymentRefunds(**data)

class PaymentTestChargeVoidSchema(Schema):
    booking_id = fields.Integer(required=True)

class PaymentTestRefundSchema(Schema):
    transaction_id = fields.String(required=True)
    amount = fields.Float(required=True)