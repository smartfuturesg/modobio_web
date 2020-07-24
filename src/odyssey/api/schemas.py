from datetime import datetime
from hashlib import md5
import statistics

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
from odyssey.models.trainer import PowerAssessment, StrengthAssessment, MoxyRipTest, MoxyAssessment, MovementAssessment
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

    clientid = fields.Integer(required=False)
    timestamp = fields.DateTime()
    isa_right = fields.Boolean()
    isa_left = fields.Boolean()
    isa_structure = fields.String(description=f"must be one of {isa_structure_list}")
    isa_dynamic = fields.Boolean()
    shoulder = fields.Nested(ChessBoardShoulderSchema)
    hip = fields.Nested(ChessBoardHipSchema)
    notes = fields.String(description="some notes regarding this assessment")


    @validates('isa_structure')
    def isa_structure_picklist(self,value):
        if not value in self.isa_structure_list:
            raise ValidationError(f'isa_structure entry invalid. Please use one of the following: {self.isa_structure_list}')

    @post_load
    def unravel(self, data, **kwargs):
        """takes anested dictionary (json input) and flattens it out 
            in order to shape into the Chessboard table
        """
        flat_data = {'clientid': data['clientid'],
                    'timestamp': datetime.utcnow(),
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
                    'isa_right': data['isa_right'],
                    'isa_left':  data['isa_left'],
                    'isa_structure': data['isa_structure'],
                    'isa_dynamic': data['isa_dynamic'],
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
                  'timestamp': data.timestamp,
                  'notes': data.notes,
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


"""
    Schemas for the trainer's API
"""

class PowerAttemptsPushPull(Schema):
    weight = fields.Integer(description="weight of exercise in PSI", validate=validate.Range(min=0, max=60))
    attempt_1 = fields.Integer(description="", validate=validate.Range(min=0, max=4000))
    attempt_2 = fields.Integer(description="", validate=validate.Range(min=0, max=4000))
    attempt_3 = fields.Integer(description="",validate=validate.Range(min=0, max=4000))
    average = fields.Float(description="",validate=validate.Range(min=0, max=4000))

class PowerAttemptsLegPress(Schema):
    weight = fields.Integer(description="weight of exercise in PSI", validate=validate.Range(min=0, max=1500))
    attempt_1 = fields.Integer(description="", validate=validate.Range(min=0, max=9999))
    attempt_2 = fields.Integer(description="", validate=validate.Range(min=0, max=9999))
    attempt_3 = fields.Integer(description="",validate=validate.Range(min=0, max=9999))
    average = fields.Float(description="",validate=validate.Range(min=0, max=9999))

class PowerPushPull(Schema):
    left = fields.Nested(PowerAttemptsPushPull)
    right = fields.Nested(PowerAttemptsPushPull)

class PowerLegPress(Schema):
    left = fields.Nested(PowerAttemptsLegPress)
    right = fields.Nested(PowerAttemptsLegPress)
    bilateral = fields.Nested(PowerAttemptsLegPress)

class PowerAssessmentSchema(Schema):
    clientid = fields.Integer()
    timestamp = fields.DateTime()
    push_pull = fields.Nested(PowerPushPull)
    leg_press = fields.Nested(PowerLegPress)
    upper_watts_per_kg = fields.Float(description = "watts per kg upper body", validate=validate.Range(min=0, max=100))
    lower_watts_per_kg = fields.Float(description = "watts per kg upper body", validate=validate.Range(min=0, max=250))

    @post_load
    def unravel(self, data, **kwargs):
        flat_data = {'clientid': data['clientid'],
                    'timestamp': datetime.utcnow(),
                    'keiser_upper_r_weight': data['push_pull']['right']['weight'],
                    'keiser_upper_r_attempt_1': data['push_pull']['right']['attempt_1'],
                    'keiser_upper_r_attempt_2': data['push_pull']['right']['attempt_2'],
                    'keiser_upper_r_attempt_3': data['push_pull']['right']['attempt_3'],
                    'keiser_upper_l_weight':    data['push_pull']['left']['weight'],
                    'keiser_upper_l_attempt_1': data['push_pull']['left']['attempt_1'],
                    'keiser_upper_l_attempt_2': data['push_pull']['left']['attempt_2'],
                    'keiser_upper_l_attempt_3': data['push_pull']['left']['attempt_3'],
                    'keiser_lower_bi_weight': data['leg_press']['bilateral']['weight'],
                    'keiser_lower_bi_attempt_1': data['leg_press']['bilateral']['attempt_1'],
                    'keiser_lower_bi_attempt_2': data['leg_press']['bilateral']['attempt_2'],
                    'keiser_lower_bi_attempt_3': data['leg_press']['bilateral']['attempt_3'],
                    'keiser_lower_r_weight':    data['leg_press']['right']['weight'],
                    'keiser_lower_r_attempt_1': data['leg_press']['right']['attempt_1'],
                    'keiser_lower_r_attempt_2': data['leg_press']['right']['attempt_2'],
                    'keiser_lower_r_attempt_3': data['leg_press']['right']['attempt_3'],
                    'keiser_lower_l_weight':     data['leg_press']['left']['weight'],
                    'keiser_lower_l_attempt_1': data['leg_press']['left']['attempt_1'],
                    'keiser_lower_l_attempt_2': data['leg_press']['left']['attempt_2'],
                    'keiser_lower_l_attempt_3': data['leg_press']['left']['attempt_3'],
                    'upper_watts_per_kg': data['upper_watts_per_kg'],
                    'lower_watts_per_kg': data['lower_watts_per_kg']
                }
        return PowerAssessment(**flat_data)

    @pre_dump
    def ravel(self, data, **kwargs):
        nested = {'clientid': data.clientid,
                  'timestamp': data.timestamp,
                  'upper_watts_per_kg' :data.upper_watts_per_kg,
                  'lower_watts_per_kg': data.lower_watts_per_kg,
                  'push_pull': {
                                'left': {'weight': data.keiser_upper_l_weight,
                                         'attempt_1': data.keiser_upper_l_attempt_1,
                                         'attempt_2': data.keiser_upper_l_attempt_2,
                                         'attempt_3': data.keiser_upper_l_attempt_3,
                                         'average':   statistics.mean([data.keiser_upper_l_attempt_1,
                                                                       data.keiser_upper_l_attempt_2,
                                                                       data.keiser_upper_l_attempt_3
                                                                    ])
                                        },
                                'right': {'weight':   data.keiser_upper_r_weight,
                                         'attempt_1': data.keiser_upper_r_attempt_1,
                                         'attempt_2': data.keiser_upper_r_attempt_2,
                                         'attempt_3': data.keiser_upper_r_attempt_3,
                                         'average':   statistics.mean([data.keiser_upper_r_attempt_1,
                                                                       data.keiser_upper_r_attempt_2,
                                                                       data.keiser_upper_r_attempt_3
                                                                    ])
                                        },
                                },
                    'leg_press': {'right' : {'weight':   data.keiser_lower_r_weight,
                                             'attempt_1': data.keiser_lower_r_attempt_1,
                                             'attempt_2': data.keiser_lower_r_attempt_2,
                                             'attempt_3': data.keiser_lower_r_attempt_3,
                                             'average':   statistics.mean([data.keiser_lower_r_attempt_1,
                                                                           data.keiser_lower_r_attempt_2,
                                                                           data.keiser_lower_r_attempt_3
                                                                        ])
                                            },
                                  'left': {'weight':   data.keiser_lower_l_weight,
                                             'attempt_1': data.keiser_lower_l_attempt_1,
                                             'attempt_2': data.keiser_lower_l_attempt_2,
                                             'attempt_3': data.keiser_lower_l_attempt_3,
                                             'average':   statistics.mean([data.keiser_lower_l_attempt_1,
                                                                           data.keiser_lower_l_attempt_2,
                                                                           data.keiser_lower_l_attempt_3
                                                                        ])
                                            },
                                  'bilateral': {'weight':   data.keiser_lower_bi_weight,
                                             'attempt_1': data.keiser_lower_bi_attempt_1,
                                             'attempt_2': data.keiser_lower_bi_attempt_2,
                                             'attempt_3': data.keiser_lower_bi_attempt_3,
                                             'average':   statistics.mean([data.keiser_lower_bi_attempt_1,
                                                                           data.keiser_lower_bi_attempt_2,
                                                                           data.keiser_lower_bi_attempt_3
                                                                        ])
                                                }
                                 }
            
                 }
        return nested


class StrengthAttemptsPushPull(Schema):
    weight = fields.Integer(description="weight of exercise in PSI", validate=validate.Range(min=0, max=350))
    attempt_1 = fields.Integer(description="", validate=validate.Range(min=0, max=50))
    attempt_2 = fields.Integer(description="", validate=validate.Range(min=0, max=50))
    attempt_3 = fields.Integer(description="",validate=validate.Range(min=0, max=50))
    estimated_10rm = fields.Float(description="",validate=validate.Range(min=0, max=350))

class StrengthPushPull(Schema):
    notes = fields.String()
    left = fields.Nested(StrengthAttemptsPushPull)
    right = fields.Nested(StrengthAttemptsPushPull)
    bilateral = fields.Nested(StrengthAttemptsPushPull)

class StrenghtAssessmentSchema(Schema):
    clientid = fields.Integer()
    timestamp = fields.DateTime()
    upper_push = fields.Nested(StrengthPushPull)
    upper_pull = fields.Nested(StrengthPushPull)

    @post_load
    def unravel(self, data, **kwargs):
        flat_data = {'clientid': data['clientid'],
                    'timestamp': datetime.utcnow(),
                    'upper_push_notes': data['upper_push']['notes'],
                    'upper_pull_notes': data['upper_pull']['notes'],
                    'upper_push_r_weight':    data['upper_push']['right']['weight'],
                    'upper_push_r_attempt_1': data['upper_push']['right']['attempt_1'],
                    'upper_push_r_attempt_2': data['upper_push']['right']['attempt_2'],
                    'upper_push_r_attempt_3': data['upper_push']['right']['attempt_3'],
                    'upper_push_r_estimated_10rm': data['upper_push']['right']['estimated_10rm'], 
                    'upper_push_l_weight':    data['upper_push']['left']['weight'],
                    'upper_push_l_attempt_1': data['upper_push']['left']['attempt_1'],
                    'upper_push_l_attempt_2': data['upper_push']['left']['attempt_2'],
                    'upper_push_l_attempt_3': data['upper_push']['left']['attempt_3'],
                    'upper_push_l_estimated_10rm': data['upper_push']['left']['estimated_10rm'], 
                    'upper_push_bi_weight':    data['upper_push']['bilateral']['weight'],
                    'upper_push_bi_attempt_1': data['upper_push']['bilateral']['attempt_1'],
                    'upper_push_bi_attempt_2': data['upper_push']['bilateral']['attempt_2'],
                    'upper_push_bi_attempt_3': data['upper_push']['bilateral']['attempt_3'],
                    'upper_push_bi_estimated_10rm': data['upper_push']['bilateral']['estimated_10rm'], 
                    'upper_pull_r_weight':    data['upper_pull']['right']['weight'],
                    'upper_pull_r_attempt_1': data['upper_pull']['right']['attempt_1'],
                    'upper_pull_r_attempt_2': data['upper_pull']['right']['attempt_2'],
                    'upper_pull_r_attempt_3': data['upper_pull']['right']['attempt_3'],
                    'upper_pull_r_estimated_10rm': data['upper_pull']['right']['estimated_10rm'], 
                    'upper_pull_l_weight':    data['upper_pull']['left']['weight'],
                    'upper_pull_l_attempt_1': data['upper_pull']['left']['attempt_1'],
                    'upper_pull_l_attempt_2': data['upper_pull']['left']['attempt_2'],
                    'upper_pull_l_attempt_3': data['upper_pull']['left']['attempt_3'],
                    'upper_pull_l_estimated_10rm': data['upper_pull']['left']['estimated_10rm'],  
                    'upper_pull_bi_weight':    data['upper_pull']['bilateral']['weight'],
                    'upper_pull_bi_attempt_1': data['upper_pull']['bilateral']['attempt_1'],
                    'upper_pull_bi_attempt_2': data['upper_pull']['bilateral']['attempt_2'],
                    'upper_pull_bi_attempt_3': data['upper_pull']['bilateral']['attempt_3']  ,
                    'upper_pull_bi_estimated_10rm': data['upper_pull']['bilateral']['estimated_10rm']                  
                }
        return StrengthAssessment(**flat_data)

    @pre_dump
    def ravel(self, data, **kwargs):
        nested = {"clientid": data.clientid,
                "timestamp": data.timestamp,
                "upper_push": {
                                "bilateral": {
                                                "attempt_3": data.upper_push_bi_attempt_3,
                                                "weight": data.upper_push_bi_weight,
                                                "attempt_2": data.upper_push_bi_attempt_2,
                                                "estimated_10rm": data.upper_push_bi_estimated_10rm,
                                                "attempt_1": data.upper_push_bi_attempt_1
                                },
                                "right": {
                                            "attempt_3": data.upper_push_r_attempt_3,
                                            "weight": data.upper_push_r_weight,
                                            "attempt_2": data.upper_push_r_attempt_2,
                                            "estimated_10rm": data.upper_push_r_estimated_10rm,
                                            "attempt_1": data.upper_push_r_attempt_1
                                },
                                "notes": data.upper_push_notes,
                                "left": {
                                            "attempt_3": data.upper_push_l_attempt_3,
                                            "weight": data.upper_push_l_weight,
                                            "attempt_2": data.upper_push_l_attempt_2,
                                            "estimated_10rm": data.upper_push_l_estimated_10rm,
                                            "attempt_1": data.upper_push_l_attempt_1
                                    }
                    },
                "upper_pull": {
                                "bilateral": {
                                                "attempt_3": data.upper_pull_bi_attempt_3,
                                                "weight": data.upper_pull_bi_weight,
                                                "attempt_2": data.upper_pull_bi_attempt_2,
                                                "estimated_10rm": data.upper_pull_bi_estimated_10rm,
                                                "attempt_1": data.upper_pull_bi_attempt_1
                                },
                                "right": {
                                            "attempt_3": data.upper_pull_r_attempt_3,
                                            "weight": data.upper_pull_r_weight,
                                            "attempt_2": data.upper_pull_r_attempt_2,
                                            "estimated_10rm": data.upper_pull_r_estimated_10rm,
                                            "attempt_1": data.upper_pull_r_attempt_1
                                },
                                "notes": data.upper_pull_notes,
                                "left": {
                                            "attempt_3": data.upper_pull_l_attempt_3,
                                            "weight": data.upper_pull_l_weight,
                                            "attempt_2": data.upper_pull_l_attempt_2,
                                            "estimated_10rm": data.upper_pull_l_estimated_10rm,
                                            "attempt_1": data.upper_pull_l_attempt_1
                                }
                            }
                    }
        return nested