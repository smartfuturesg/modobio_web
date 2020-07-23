from datetime import datetime
from hashlib import md5

from marshmallow import Schema, fields, post_load, ValidationError, validates, validate
from marshmallow import post_load, post_dump, pre_dump

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
from odyssey.models.pt import Chessboard, PTHistory
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

class SignedDocumentsSchema(Schema):
    """
        list of document urls
    """
    urls = fields.List(fields.String())

class ShoulderRotationSchema(Schema):
    ir = fields.Integer(description="internal rotation", validate=validate.Range(min=0, max=100))
    er = fields.Integer(description="external rotation", validate=validate.Range(min=0, max=130))
    abd = fields.Integer(description="abduction", validate=validate.Range(min=0, max=75))
    add = fields.Integer(description="adduction", validate=validate.Range(min=0, max=135))
    flexion  = fields.Integer(validate=validate.Range(min=0, max=190))
    extension  = fields.Integer(validate=validate.Range(min=0, max=75))

class HipRotationSchema(Schema):
    ir = fields.Integer(description="internal rotation", validate=validate.Range(min=0, max=60))
    er = fields.Integer(description="external rotation", validate=validate.Range(min=0, max=90))
    abd = fields.Integer(description="abduction", validate=validate.Range(min=0, max=75))
    add = fields.Integer(description="adduction",validate=validate.Range(min=0, max=50))
    flexion  = fields.Integer(validate=validate.Range(min=0, max=160))
    extension  = fields.Integer(validate=validate.Range(min=0, max=110))
    slr  = fields.Integer(validate=validate.Range(min=0, max=120))

class ChessBoardShoulderSchema(Schema):
    left = fields.Nested(ShoulderRotationSchema)
    right = fields.Nested(ShoulderRotationSchema)

class ChessBoardHipSchema(Schema):
    left = fields.Nested(HipRotationSchema)
    right = fields.Nested(HipRotationSchema)

class ChessboardSchema(Schema):
    isa_structure_list  = ['Inhaled','Exhaled', 'Asymettrical Normal','Asymettrical Atypical']

    # clientid = fields.Integer
    clientid = fields.Integer(required=False)
    timestamp = fields.DateTime()
    isa_right = fields.Boolean()
    isa_left = fields.Boolean()
    isa_structure = fields.String(description=f"must be one of {isa_structure_list}")
    isa_dynamic = fields.Boolean()
    shoulder = fields.Nested(ChessBoardShoulderSchema)
    hip = fields.Nested(ChessBoardHipSchema)


    @validates('isa_structure')
    def isa_structure_picklist(self,value):
        if not value in self.isa_structure_list:
            raise ValidationError(f'isa_structure entry invalid. Please use one of the following: {self.isa_structure_list}')

    @post_load
    def unravel(self, data, **kwargs):
        flat_data = {'clientid': data['clientid'],
                    'timestamp': datetime.utcnow(),
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
                    'isa_right': data['isa_right'],
                    'isa_left':  data['isa_left'],
                    'isa_structure': data['isa_structure'],
                    'isa_dynamic': data['isa_dynamic'],
                    }        
        return Chessboard(**flat_data)

    @pre_dump
    def ravel(self, data, **kwargs):
        shoulder_l = {k.split('_')[-1]:v for k,v in data.__dict__.items() if 'left_shoulder' in k}
        shoulder_r = {k.split('_')[-1]:v for k,v in data.__dict__.items() if 'right_shoulder' in k}
        hip_l = {k.split('_')[-1]:v for k,v in data.__dict__.items() if 'left_hip' in k}
        hip_r = {k.split('_')[-1]:v for k,v in data.__dict__.items() if 'right_hip' in k}
        nested = {'clientid': data.clientid,
                  'timestamp': data.timestamp,
                  'isa_left' :data.isa_left,
                  'isa_right': data.isa_right,
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
