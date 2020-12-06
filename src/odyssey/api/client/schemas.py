from datetime import datetime
from marshmallow import (
    Schema, 
    fields, 
    post_load,
    pre_dump,
    ValidationError, 
    validates, 
    validate
)

from odyssey import ma
from odyssey.api.user.models import User
from odyssey.api.client.models import (
    ClientConsent,
    ClientConsultContract,
    ClientInfo,
    ClientIndividualContract, 
    ClientPolicies,
    ClientRelease,
    ClientReleaseContacts,
    ClientSubscriptionContract,
    ClientFacilities,
)
from odyssey.api.user.schemas import UserInfoPutSchema

class ClientSearchItemsSchema(Schema):
    user_id = fields.Integer()
    firstname = fields.String(required=False, validate=validate.Length(min=1, max= 50), missing=None)
    lastname = fields.String(required=False, validate=validate.Length(min=1,max=50), missing=None)
    email = fields.Email(required=False, missing=None)
    phone = fields.String(required=False, validate=validate.Length(min=0,max=50), missing=None)
    dob = fields.Date(required=False, missing=None)
    record_locator_id = fields.String(required=False, validate=validate.Length(min=0,max=10), missing=None)
    modobio_id = fields.String(required=False, validate=validate.Length(min=0,max=12), missing=None)

class ClientSearchMetaSchema(Schema):
    page = fields.Integer(required=False, missing=0)
    per_page = fields.Integer(required=False, missing=0)
    total_pages = fields.Integer(required=False, missing=0)
    total_items = fields.Integer(required=False, missing=0)

class ClientSearchLinksSchema(Schema):
    _self = fields.String(required=False, validate=validate.Length(min=1, max= 50), missing=None)
    _next = fields.String(required=False, validate=validate.Length(min=1, max= 50), missing=None)
    _prev = fields.String(required=False, validate=validate.Length(min=1, max= 50), missing=None)

class ClientSearchOutSchema(Schema):
    """ ClientSearchOutSchema uses nested ClientSearchItemsSchemas and 
        ClientSearchMetaSchemas """
    items = fields.Nested(ClientSearchItemsSchema(many=True),
                            missing=ClientSearchItemsSchema().load({}))
    _meta = fields.Nested(ClientSearchMetaSchema, missing=ClientSearchMetaSchema().load({}))
    _links = fields.Nested(ClientSearchLinksSchema, missing=ClientSearchLinksSchema().load({}))
    
class ClientFacilitiesSchema(Schema):

    idx = fields.Integer()
    user_id = fields.Integer()
    facility_id = fields.Integer()

    @post_load
    def make_object(self, data, **kwargs):
        return ClientFacilities(**data)

class ClientInfoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClientInfo
        exclude = ('created_at', 'updated_at', 'idx')
        dump_only = ('modobio_id', 'membersince')

    user_id = fields.Integer()

    @post_load
    def make_object(self, data, **kwargs):
        return ClientInfo(**data)

class ClientInfoPutSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClientInfo
        exclude = ('created_at', 'updated_at', 'idx')
        dump_only = ('modobio_id', 'membersince', 'is_staff', 'is_client', 'user_id', 'receive_docs')

class ClientAndUserInfoSchema(Schema):

    client_info = fields.Nested(ClientInfoPutSchema, required=False, missing={})
    user_info = fields.Nested(UserInfoPutSchema, required=False, missing={})

class NewRemoteClientSchema(Schema):

    email = fields.Email()
    firstname = fields.String(required=True, validate=validate.Length(min=1, max= 50))
    lastname = fields.String(required=True, validate=validate.Length(min=1,max=50))
    middlename = fields.String(required=False, validate=validate.Length(min=0,max=50))

    @post_load
    def make_object(self, data, **kwargs):
        return ClientInfo(**data)
        
#class ClientRemoteRegistrationPortalSchema(Schema):
#    """
#        holds client's access information for remote registration
#    """
#    email = fields.Email()
#    user_id = fields.Integer()
#    password = fields.String(dump_only=True)
#    registration_portal_expiration = fields.DateTime(dump_only=True)
#    registration_portal_id = fields.String(dump_only=True)
#
#    @post_load
#    def make_object(self, data, **kwargs):
#        remote_client_portal = RemoteRegistration(user_id=data["user_id"], email=data["email"])
#        remote_client_portal.set_password()
#        remote_client_portal.get_temp_registration_endpoint()
#        return remote_client_portal


#class RefreshRemoteRegistrationSchema(Schema):
#    """
#        refresh the remote registration password and link for the client
#        with the provided email
#    """
#    email = fields.Email(required=True)

class ClientConsentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClientConsent
    
    user_id = fields.Integer(missing=0)

    @post_load
    def make_object(self, data, **kwargs):
        return ClientConsent(**data)

class ClientReleaseContactsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClientReleaseContacts
        exclude = ('idx',)

    user_id = fields.Integer(missing=0)
    release_contract_id = fields.Integer()
    release_direction = fields.String(description="Direction must be either 'TO' (release to) or 'FROM' (release from)")

    @post_load
    def make_object(self, data, **kwargs):
        return ClientReleaseContacts(**data)

    @validates('release_direction')
    def release_direction_picklist(self,value):
        direction_values=['TO', 'FROM']
        if not value in direction_values:
            raise ValidationError(f'release_direction entry invalid. Please use one of the following: {direction_values}')

class ClientReleaseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClientRelease

    release_to = fields.Nested(ClientReleaseContactsSchema, many=True)
    release_from = fields.Nested(ClientReleaseContactsSchema, many=True)
    
    user_id = fields.Integer(missing=0)

    @post_load
    def make_object(self, data, **kwargs):
        data.pop("release_to")
        data.pop("release_from")
        return ClientRelease(**data)

    @pre_dump
    def ravel(self, data, **kwargs):
        """
        nest release contacts objects into release contract
        """
        data_ravel = data.__dict__

        release_to  = ClientReleaseContacts.query.filter_by(release_contract_id = data.idx, release_direction = 'TO').all()
        release_from  = ClientReleaseContacts.query.filter_by(release_contract_id = data.idx, release_direction = 'FROM').all()

        release_to_list = [obj.__dict__ for obj in release_to]
        release_from_list = [obj.__dict__ for obj in release_from]

        data_ravel["release_to"] = release_to_list
        data_ravel["release_from"] = release_from_list
        return data

class SignAndDateSchema(Schema):
    """for marshaling signatures and sign dates into objects (contracts) requiring only a signature"""

    user_id = fields.Integer(missing=0, dump_only=True)
    signdate = fields.Date(format="iso", required=True)
    signature = fields.String(required=True)

class ClientSubscriptionContractSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClientSubscriptionContract
    
    user_id = fields.Integer(missing=0)

    @post_load
    def make_object(self, data, **kwargs):
        return ClientSubscriptionContract(
                    user_id = data["user_id"],
                    signature=data["signature"],
                    signdate=data["signdate"]
                    )

class ClientConsultContractSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClientConsultContract
    
    user_id = fields.Integer(missing=0)

    @post_load
    def make_object(self, data, **kwargs):
        return ClientConsultContract(
                    user_id = data["user_id"],
                    signature=data["signature"],
                    signdate=data["signdate"]
                    )
    
class ClientPoliciesContractSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClientPolicies
    
    user_id = fields.Integer(missing=0)

    @post_load
    def make_object(self, data, **kwargs):
        return ClientPolicies(
                    user_id = data["user_id"],
                    signature=data["signature"],
                    signdate=data["signdate"]
                    )
    

class ClientIndividualContractSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClientIndividualContract
        
    user_id = fields.Integer(missing=0)
    @post_load
    def make_object(self, data, **kwargs):
        return ClientIndividualContract(**data)

class SignedDocumentsSchema(Schema):
    """ Dictionary of all signed documents and the URL to the PDF file. """
    urls = fields.Dict(
        keys=fields.String(description='Document display name'),
        values=fields.String(description='URL to PDF file of document.')
    )

class OutstandingForm(Schema):
    """
        Forms that have not yet been completed
        Display name and URI given
    """
    name = fields.String(description='name of form')
    URI = fields.String(description = 'URI for completing form')

class ClientRegistrationStatusSchema(Schema):

    outstanding = fields.Nested(OutstandingForm(many=True))


class ClientDataTierSchema(Schema):

    user_id = fields.Integer(missing=None)
    stored_bytes = fields.Integer(description="total bytes stored for the client", missing=None)
    tier = fields.String(description="data storage tier. Either Tier 1/2/3", missing=None)

class ClientClinicalCareTeamInternalSchema(Schema):
    """
    Schema is used for serializing/deserializing clinical care team related payloads
    """
    team_member_email = fields.Email(description="email for clinical care team member")
    team_member_user_id = fields.Integer(description="user_id for clinical care team member", dump_only=True)

class ClientClinicalCareTeamSchema(Schema):
    """
    Schema is used for nesting ClientClinicalCareTeamInternalSchema 
    """
    
    care_team = fields.Nested(ClientClinicalCareTeamInternalSchema(many=True), missing=[])
    total_items = fields.Integer(dump_only=True)

class AllClientsDataTier(Schema):

    items = fields.Nested(ClientDataTierSchema(many=True), missing=ClientDataTierSchema().load({}))
    total_stored_bytes = fields.Integer(description="Total bytes stored for all clients", missing=0)
    total_items = fields.Integer(description="number of clients in this payload", missing=0)
