from marshmallow import Schema, fields, post_load, validate

from odyssey import ma
from odyssey.api.payment.models import PaymentMethods, PaymentStatus, PaymentRefunds, PaymentHistory
from odyssey.utils.base.schemas import BaseSchema

class PaymentMethodsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PaymentMethods
        dump_only = ('created_at', 'updated_at', 'idx', 'payment_id', 'payment_type', 'number')

    token = fields.String(load_only=True, required=True)
    expiration = fields.String(load_only=True, required=True)

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

    @post_load
    def make_object(self, data, **kwargs):
        return PaymentHistory(**data)

class PaymentRefundsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PaymentRefunds
        exclude = ('created_at', 'updated_at', 'idx')

    payment_id = fields.Integer(required=True)
    refund_reason = fields.String(validate=validate.Length(min=1))
    
    @post_load
    def make_object(self, data, **kwargs):
        return PaymentRefunds(**data)