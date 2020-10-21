from datetime import datetime
from hashlib import md5
from marshmallow import Schema, fields, post_load, ValidationError, validates, validate
from marshmallow import post_load, post_dump, pre_dump, pre_load

from odyssey import ma
from odyssey.models.doctor import ( 
    MedicalHistory,
    MedicalPhysicalExam,
    MedicalImaging,
    MedicalBloodTests,
    MedicalBloodTestResults,
    MedicalBloodTestResultTypes
)
from odyssey.models.client import (
    ClientConsent,
    ClientConsultContract,
    ClientExternalMR,
    ClientInfo,
    ClientIndividualContract, 
    ClientPolicies,
    ClientRelease,
    ClientReleaseContacts,
    ClientSubscriptionContract,
    ClientFacilities,
    RemoteRegistration
)
from odyssey.models.misc import MedicalInstitutions, RegisteredFacilities
from odyssey.models.pt import Chessboard, PTHistory
from odyssey.models.staff import Staff
from odyssey.models.trainer import (
    FitnessQuestionnaire,
    HeartAssessment, 
    PowerAssessment, 
    StrengthAssessment, 
    MoxyRipTest, 
    MoxyAssessment, 
    MovementAssessment,
    LungAssessment
)
from odyssey.models.wearables import Wearables, WearablesOura, WearablesFreeStyle
from odyssey.utils.misc import list_average

class ClientSearchItemsSchema(Schema):
    clientid = fields.Integer()
    firstname = fields.String(required=False, validate=validate.Length(min=1, max= 50), missing=None)
    lastname = fields.String(required=False, validate=validate.Length(min=1,max=50), missing=None)
    email = fields.Email(required=False, missing=None)
    phone = fields.String(required=False, validate=validate.Length(min=0,max=50), missing=None)
    dob = fields.Date(required=False, missing=None)
    record_locator_id = fields.String(required=False, validate=validate.Length(min=0,max=10), missing=None)

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
    client_id = fields.Integer()
    facility_id = fields.Integer()

    @post_load
    def make_object(self, data, **kwargs):
        return ClientFacilities(**data)

class ClientInfoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClientInfo

    record_locator_id = fields.String(missing=None)

    @post_load
    def make_object(self, data, **kwargs):
        return ClientInfo(**data)

class NewRemoteClientSchema(Schema):

    email = fields.Email()
    firstname = fields.String(required=True, validate=validate.Length(min=1, max= 50))
    lastname = fields.String(required=True, validate=validate.Length(min=1,max=50))
    middlename = fields.String(required=False, validate=validate.Length(min=0,max=50))

    @post_load
    def make_object(self, data, **kwargs):
        return ClientInfo(**data)
        
class ClientRemoteRegistrationPortalSchema(Schema):
    """
        holds client's access information for remote registration
    """
    email = fields.Email()
    clientid = fields.Integer()
    password = fields.String(dump_only=True)
    registration_portal_expiration = fields.DateTime(dump_only=True)
    registration_portal_id = fields.String(dump_only=True)

    @post_load
    def make_object(self, data, **kwargs):
        remote_client_portal = RemoteRegistration(clientid=data["clientid"], email=data["email"])
        remote_client_portal.set_password()
        remote_client_portal.get_temp_registration_endpoint()
        return remote_client_portal


class RefreshRemoteRegistrationSchema(Schema):
    """
        refresh the remote registration password and link for the client
        with the provided email
    """
    email = fields.Email(required=True)

class ClientConsentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClientConsent
    
    clientid = fields.Integer(missing=0)

    @post_load
    def make_object(self, data, **kwargs):
        return ClientConsent(**data)

class ClientReleaseContactsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClientReleaseContacts
        exclude = ('idx',)

    clientid = fields.Integer(missing=0)
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
    
    clientid = fields.Integer(missing=0)

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

    clientid = fields.Integer(missing=0, dump_only=True)
    signdate = fields.Date(format="iso", required=True)
    signature = fields.String(required=True)

class ClientSubscriptionContractSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClientSubscriptionContract
    
    clientid = fields.Integer(missing=0)

    @post_load
    def make_object(self, data, **kwargs):
        return ClientSubscriptionContract(
                    clientid = data["clientid"],
                    signature=data["signature"],
                    signdate=data["signdate"]
                    )

class ClientConsultContractSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClientConsultContract
    
    clientid = fields.Integer(missing=0)

    @post_load
    def make_object(self, data, **kwargs):
        return ClientConsultContract(
                    clientid = data["clientid"],
                    signature=data["signature"],
                    signdate=data["signdate"]
                    )
    
class ClientPoliciesContractSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClientPolicies
    
    clientid = fields.Integer(missing=0)

    @post_load
    def make_object(self, data, **kwargs):
        return ClientPolicies(
                    clientid = data["clientid"],
                    signature=data["signature"],
                    signdate=data["signdate"]
                    )
    

class ClientIndividualContractSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClientIndividualContract
        
    clientid = fields.Integer(missing=0)
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

    clientid = fields.Integer(missing=None)
    stored_bytes = fields.Integer(description="total bytes stored for the client", missing=None)
    tier = fields.String(description="data storage tier. Either Tier 1/2/3", missing=None)


class AllClientsDataTier(Schema):

    items = fields.Nested(ClientDataTierSchema(many=True), missing=ClientDataTierSchema().load({}))
    total_stored_bytes = fields.Integer(description="Total bytes stored for all clients", missing=0)
    total_items = fields.Integer(description="number of clients in this payload", missing=0)

"""
    Schemas for the pt API
"""

class PTHistorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PTHistory
        
    clientid = fields.Integer(missing=0)
    
    @post_load
    def make_object(self, data, **kwargs):
        return PTHistory(**data)



class ShoulderRotationSchema(Schema):
    ir = fields.Integer(description="internal rotation", validate=validate.Range(min=0, max=100), missing=None)
    er = fields.Integer(description="external rotation", validate=validate.Range(min=0, max=130), missing=None)
    abd = fields.Integer(description="abduction", validate=validate.Range(min=0, max=75), missing=None)
    add = fields.Integer(description="adduction", validate=validate.Range(min=0, max=135), missing=None)
    flexion  = fields.Integer(validate=validate.Range(min=0, max=190), missing=None)
    extension  = fields.Integer(validate=validate.Range(min=0, max=75), missing=None)

class HipRotationSchema(Schema):
    ir = fields.Integer(description="internal rotation", validate=validate.Range(min=0, max=60), missing=None)
    er = fields.Integer(description="external rotation", validate=validate.Range(min=0, max=90), missing=None)
    abd = fields.Integer(description="abduction", validate=validate.Range(min=0, max=75), missing=None)
    add = fields.Integer(description="adduction",validate=validate.Range(min=0, max=50), missing=None)
    flexion  = fields.Integer(validate=validate.Range(min=0, max=160), missing=None)
    extension  = fields.Integer(validate=validate.Range(min=0, max=110), missing=None)
    slr  = fields.Integer(validate=validate.Range(min=0, max=120), missing=None)

class ChessBoardShoulderSchema(Schema):
    left = fields.Nested(ShoulderRotationSchema, missing = ShoulderRotationSchema().load({}))
    right = fields.Nested(ShoulderRotationSchema, missing = ShoulderRotationSchema().load({}))

class ChessBoardHipSchema(Schema):
    left = fields.Nested(HipRotationSchema, missing = HipRotationSchema().load({}))
    right = fields.Nested(HipRotationSchema, missing = HipRotationSchema().load({}))

class ChessboardSchema(Schema):
    isa_structure_list  = ['Inhaled','Exhaled', 'Asymmetrical Normal','Asymmetrical Atypical']
    isa_movement_list  = ['Dynamic', 'Static', 'R Static/Left Dynamic', 'L Static/Right Dynamic']

    clientid = fields.Integer(missing=0)
    timestamp = fields.DateTime()
    isa_structure = fields.String(description=f"must be one of {isa_structure_list}", missing=None)
    isa_movement = fields.String(description=f"must be one of {isa_movement_list}", missing=None)
    co2_tolerance = fields.Integer(validate=validate.Range(min=0, max=120), missing=None)
    shoulder = fields.Nested(ChessBoardShoulderSchema, missing=ChessBoardShoulderSchema().load({}))
    hip = fields.Nested(ChessBoardHipSchema, missing=ChessBoardHipSchema().load({}))
    notes = fields.String(description="some notes regarding this assessment", missing=None)


    @validates('isa_structure')
    def isa_structure_picklist(self,value):
        if not value in self.isa_structure_list and value is not None:
            raise ValidationError(f'isa_structure entry invalid. Please use one of the following: {self.isa_structure_list}')

    @validates('isa_movement')
    def isa_movement_picklist(self,value):
        if not value in self.isa_movement_list and value is not None:
            raise ValidationError(f'isa_movement entry invalid. Please use one of the following: {self.isa_movement_list}')

    @post_load
    def unravel(self, data, **kwargs):
        """takes a nested dictionary (json input) and flattens it out
            in order to shape into the Chessboard table
        """
        flat_data = {'clientid': data['clientid'],
                    'notes': data['notes'],
                    'left_shoulder_er': data['shoulder']['left']['er'],
                    'left_shoulder_ir': data['shoulder']['left']['ir'],
                    'left_shoulder_abd': data['shoulder']['left']['abd'],
                    'left_shoulder_add': data['shoulder']['left']['add'],
                    'left_shoulder_flexion':   data['shoulder']['left']['flexion'],
                    'left_shoulder_extension': data['shoulder']['left']['extension'],
                    'right_shoulder_er':  data['shoulder']['right']['er'],
                    'right_shoulder_ir':  data['shoulder']['right']['ir'],
                    'right_shoulder_abd': data['shoulder']['right']['abd'],
                    'right_shoulder_add': data['shoulder']['right']['add'],
                    'right_shoulder_flexion':   data['shoulder']['right']['flexion'],
                    'right_shoulder_extension': data['shoulder']['right']['extension'],
                    'left_hip_slr': data['hip']['left']['slr'],
                    'left_hip_er':  data['hip']['left']['er'],
                    'left_hip_ir':  data['hip']['left']['ir'],
                    'left_hip_abd': data['hip']['left']['abd'],
                    'left_hip_add': data['hip']['left']['add'],
                    'left_hip_flexion':   data['hip']['left']['flexion'],
                    'left_hip_extension': data['hip']['left']['extension'],
                    'right_hip_slr': data['hip']['right']['slr'],
                    'right_hip_er':  data['hip']['right']['er'],
                    'right_hip_ir':  data['hip']['right']['ir'],
                    'right_hip_abd': data['hip']['right']['abd'],
                    'right_hip_add': data['hip']['right']['add'],
                    'right_hip_flexion':   data['hip']['right']['flexion'],
                    'right_hip_extension': data['hip']['right']['extension'],
                    'isa_structure': data['isa_structure'],
                    'isa_movement': data['isa_movement']
                    }        
        return Chessboard(**flat_data)

    @pre_dump
    def ravel(self, data, **kwargs):
        """converts the flat Chessboard table into a nested dictionary for easier
            procesing on the fron end
        """
        shoulder_l = {k.split('_')[-1]:v for k,v in data.__dict__.items() if 'left_shoulder' in k} 
        shoulder_r = {k.split('_')[-1]:v for k,v in data.__dict__.items() if 'right_shoulder' in k}
        hip_l = {k.split('_')[-1]:v for k,v in data.__dict__.items() if 'left_hip' in k}
        hip_r = {k.split('_')[-1]:v for k,v in data.__dict__.items() if 'right_hip' in k}
        nested = {'clientid': data.clientid,
                  'notes': data.notes,
                  'isa_structure': data.isa_structure,
                  'isa_movement': data.isa_movement,
                  'shoulder': {
                                'right': shoulder_r,
                               'left': shoulder_l
                               },
                  'hip': {
                           'right': hip_r,
                           'left': hip_l
                        }
                  }
        return nested



#
#   Schemas for the wearables API
#
class WearablesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Wearables
        load_instance = True
        exclude = ('idx', 'clientid', 'created_at', 'updated_at')


class WearablesOuraAuthSchema(Schema):
    oura_client_id = fields.String()
    oauth_state = fields.String()


class WearablesFreeStyleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WearablesFreeStyle
        load_instance = True
        exclude = ('idx', 'clientid', 'created_at', 'updated_at')


class WearablesFreeStyleActivateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WearablesFreeStyle
        load_instance = True
        fields = ('activation_timestamp',)
