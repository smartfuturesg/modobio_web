from marshmallow import Schema, fields, post_load

from odyssey import ma
from odyssey.api.payment.models import PaymentMethods, PaymentStatus

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

    request_amount = fields.String()
    user_id = fields.Integer()

    @post_load
    def make_object(self, data, **kwargs):
        return PaymentStatus(**data)

class PaymentStatusOutputSchema(Schema):

    payment_statuses = fields.Nested(PaymentStatusSchema(many=True))