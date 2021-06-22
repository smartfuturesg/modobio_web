from marshmallow import Schema, fields, post_load

from odyssey import ma
from odyssey.api.payment.models import PaymentMethods
from odyssey.utils.base.schemas import BaseSchema

class PaymentMethodsSchema(BaseSchema):
    class Meta:
        model = PaymentMethods

    @post_load
    def make_object(self, data, **kwargs):
        return PaymentMethods(**data)