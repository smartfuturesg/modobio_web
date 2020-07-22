from datetime import datetime
from hashlib import md5

from marshmallow import Schema, fields, post_load, ValidationError, validates, validate
from marshmallow import post_load, post_dump

from odyssey import ma
from odyssey.models.intake import (
    ClientConsent,
    ClientInfo,
    ClientConsultContract,
    RemoteRegistration, 
    ClientIndividualContract, 
    ClientPolicies,
    ClientRelease,
    ClientSubscriptionContract
)
from odyssey.constants import DOCTYPE, DOCTYPE_DOCREV_MAP

class ClientInfoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClientInfo

    record_locator_id = fields.String(dump_only=True)

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
        
class ClientSummarySchema(Schema):

    clientid = fields.Integer(required=True)
    record_locator_id = fields.String(dump_only=True)
    email = fields.Email()
    firstname = fields.String(required=True, validate=validate.Length(min=1, max= 50))
    lastname = fields.String(required=True, validate=validate.Length(min=1,max=50))
    middlename = fields.String(required=False, validate=validate.Length(min=1,max=50))
    phone = fields.String()

    _links = fields.Dict()

    @post_dump
    def add_record_locator_id(self,data, **kwargs ):
        name_hash = md5(bytes((data['firstname']+data['lastname']), 'utf-8')).hexdigest()
        data['record_locator_id'] = (data['firstname'][0]+data['lastname'][0]+str(data['clientid'])+name_hash[0:6]).upper()

        # data['_links']= {
        #     'self': api.url_for(Clients, page=page, per_page=per_page),
        #     'next': api.url_for(Clients, page=page + 1, per_page=per_page)
        #     if resources.has_next else None,
        #     'prev': api.url_for(Clients, page=page - 1, per_page=per_page)
        #     if resources.has_prev else None,
        # }
        return data


class ClientConsentSchema(ma.SQLAlchemyAutoSchema):
    doctype = DOCTYPE.consent
    docrev = DOCTYPE_DOCREV_MAP[doctype]
    class Meta:
        model = ClientConsent
    
    # workaround for foreign fields as they are not picked up in autoschema
    clientid = fields.Integer(required=False)

    @post_load
    def make_object(self, data, **kwargs):
        data["revision"] = self.docrev
        return ClientConsent(**data)

class ClientReleaseSchema(ma.SQLAlchemyAutoSchema):
    doctype = DOCTYPE.release
    docrev = DOCTYPE_DOCREV_MAP[doctype]
    class Meta:
        model = ClientRelease
    
    # workaround for foreign fields as they are not picked up in autoschema
    clientid = fields.Integer(required=False)

    @post_load
    def make_object(self, data, **kwargs):
        data["revision"] = self.docrev
        return ClientRelease(**data)

class SignAndDateSchema(Schema):
    """for marshaling signatures and sign dates into objects (contracts) requiring only a signature"""

    clientid = fields.Integer(dump_only=True)
    signdate = fields.Date(format="iso", required=True)
    signature = fields.String(required=True)

class ClientSubscriptionContractSchema(ma.SQLAlchemyAutoSchema):
    doctype = DOCTYPE.subscription
    docrev = DOCTYPE_DOCREV_MAP[doctype]
    class Meta:
        model = ClientSubscriptionContract
    
    clientid = fields.Integer(required=True)

    @post_load
    def make_object(self, data, **kwargs):
        return ClientSubscriptionContract(
                    clientid = data["clientid"],
                    signature=data["signature"],
                    signdate=data["signdate"],
                    revision=self.docrev
                    )

class ClientConsultContractSchema(ma.SQLAlchemyAutoSchema):
    doctype = DOCTYPE.consult
    docrev = DOCTYPE_DOCREV_MAP[doctype]
    class Meta:
        model = ClientConsultContract
    
    clientid = fields.Integer(required=True)

    @post_load
    def make_object(self, data, **kwargs):
        return ClientConsultContract(
                    clientid = data["clientid"],
                    signature=data["signature"],
                    signdate=data["signdate"],
                    revision=self.docrev
                    )
    
class ClientPoliciesContractSchema(ma.SQLAlchemyAutoSchema):
    doctype = DOCTYPE.policies
    docrev = DOCTYPE_DOCREV_MAP[doctype]
    class Meta:
        model = ClientPolicies
    
    clientid = fields.Integer(required=True)

    @post_load
    def make_object(self, data, **kwargs):
        return ClientPolicies(
                    clientid = data["clientid"],
                    signature=data["signature"],
                    signdate=data["signdate"],
                    revision=self.docrev
                    )
    

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

class ClientIndividualContractSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = ClientIndividualContract

    @post_load
    def make_object(self, data, **kwargs):
        return ClientIndividualContract(**data)