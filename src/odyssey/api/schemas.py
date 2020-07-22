from datetime import datetime
from hashlib import md5

from marshmallow import Schema, fields, post_load, ValidationError, validates, validate
from marshmallow import post_load, post_dump

from odyssey import ma
from odyssey.models.intake import ClientInfo, RemoteRegistration

class ClientInfoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClientInfo

    @post_load
    def make_object(self, data, **kwargs):
        return ClientInfo(**data)

    @post_dump
    def add_record_locator_id(self,data, **kwargs ):
        name_hash = md5(bytes((data['firstname']+data['lastname']), 'utf-8')).hexdigest()
        data['record_locator_id'] = (data['firstname'][0]+data['lastname'][0]+str(data['clientid'])+name_hash[0:6]).upper()
        return data

class NewRemoteRegistrationSchema(Schema):

    email = fields.Email()
    firstname = fields.String(required=True, validate=validate.Length(min=1, max= 50))
    lastname = fields.String(required=True, validate=validate.Length(min=1,max=50))
    middlename = fields.String(required=False, validate=validate.Length(min=1,max=50))

    @post_load
    def make_object(self, data, **kwargs):
        return ClientInfo(**data)

class ClientRemoteRegistrationSchema(ma.SQLAlchemyAutoSchema):
    """
        holds client's access information for remote registration
    """
    class Meta:
        model = RemoteRegistration

class RefreshRemoteRegistrationSchema(Schema):
    """
        refresh the remote registration password and link for the client
        with the provided email
    """
    email = fields.Email(required=True)
