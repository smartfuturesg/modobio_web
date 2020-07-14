from marshmallow import post_load

from odyssey import ma
from odyssey.models.intake import ClientInfo

class ClientInfoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClientInfo

    @post_load
    def make_object(self, data, **kwargs):
        return ClientInfo(**data)
    

