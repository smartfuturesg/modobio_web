from marshmallow import Schema, fields, post_load

from odyssey import ma
from odyssey.api.payment.models import PaymentMethods
from odyssey.utils.base.schemas import BaseSchema

class PaymentMethodsSchema(BaseSchema):
    class Meta:
        model = PaymentMethods
        dump_only = ('payment_id')

    token = fields.String(load_only=True, required=True)

    @post_load
    def make_object(self, data, **kwargs):
        return PaymentMethods(**data)