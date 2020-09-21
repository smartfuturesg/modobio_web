from datetime import datetime
from hashlib import md5
import statistics

from marshmallow import Schema, fields, post_load, ValidationError, validates, validate
from marshmallow import post_load, post_dump, pre_dump, pre_load

from odyssey import ma
from odyssey.models.doctor import ( 
    MedicalHistory,
    MedicalPhysicalExam,
    MedicalBloodChemistryCMP,
    MedicalBloodChemistryCBC,
    MedicalBloodChemistryThyroid,
    MedicalImaging
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
    RemoteRegistration
)
from odyssey.models.misc import MedicalInstitutions
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
from odyssey.models.wearables import Wearables, WearablesOura
from requests_toolbelt import MultipartEncoder

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

class ClientSummarySchema(Schema):

    clientid = fields.Integer(missing=0)
    record_locator_id = fields.String(dump_only=True)
    email = fields.Email()
    firstname = fields.String(required=True, validate=validate.Length(min=1, max= 50))
    lastname = fields.String(required=True, validate=validate.Length(min=1,max=50))
    middlename = fields.String(required=False, validate=validate.Length(min=0,max=50))
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
    isa_structure_list  = ['Inhaled','Exhaled', 'Asymmetrical Normal','Asymmetrical Atypical']
    isa_movement_list  = ['Dynamic', 'Static', 'R Static/Left Dynamic', 'L Static/Right Dynamic']

    clientid = fields.Integer(missing=0)
    timestamp = fields.DateTime()
    isa_structure = fields.String(description=f"must be one of {isa_structure_list}")
    isa_movement = fields.String(description=f"must be one of {isa_movement_list}")
    co2_tolerance = fields.Integer(validate=validate.Range(min=0, max=120))
    shoulder = fields.Nested(ChessBoardShoulderSchema)
    hip = fields.Nested(ChessBoardHipSchema)
    notes = fields.String(description="some notes regarding this assessment")


    @validates('isa_structure')
    def isa_structure_picklist(self,value):
        if not value in self.isa_structure_list:
            raise ValidationError(f'isa_structure entry invalid. Please use one of the following: {self.isa_structure_list}')

    @validates('isa_movement')
    def isa_movement_picklist(self,value):
        if not value in self.isa_movement_list:
            raise ValidationError(f'isa_movement entry invalid. Please use one of the following: {self.isa_movement_list}')

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
                  'timestamp': data.timestamp,
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
    clientid = fields.Integer(missing=0)
    timestamp = fields.DateTime()
    push_pull = fields.Nested(PowerPushPull)
    leg_press = fields.Nested(PowerLegPress)
    upper_watts_per_kg = fields.Float(description = "watts per kg upper body", validate=validate.Range(min=0, max=100))
    lower_watts_per_kg = fields.Float(description = "watts per kg upper body", validate=validate.Range(min=0, max=250))
    vital_weight = fields.Float(description="weight pulled from doctor physical data", dump_only=True)

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
        # add client's vital_weight from most recent physical exam
        recent_physical = MedicalPhysicalExam.query.filter_by(clientid=data.clientid).order_by(MedicalPhysicalExam.idx.desc()).first()
        nested["vital_weight"] = recent_physical.vital_weight
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
    clientid = fields.Integer(missing=0)
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


class SquatTestSchema(Schema):
    depth = fields.String()
    ramp = fields.String()
    eye_test = fields.Boolean()
    can_breathe = fields.Boolean()
    can_look_up = fields.Boolean()

class ToeTouchTestSchema(Schema):
    pelvis_movement_test_options = ['Right Hip High','Right Hip Back','Left Hip High',
                                'Left Hip Back','Right Hip High', 'Even Bilaterally']

    ribcage_movement_test_options = ['Right Posterior Ribcage High','Right Posterior Ribcage Back',	
                                'Left Posterior Ribcage High', 'Left Posterior Ribcage Back', 'Even Bilaterally']
    depth = fields.String()
    pelvis_movement = fields.List(fields.String,
                description=f"Descriptors for this assessment must be in the following picklist: {pelvis_movement_test_options}",
                required=True) 
    ribcage_movement = fields.List(fields.String,
                description=f"Descriptors for this assessment must be in the following picklist: {ribcage_movement_test_options}",
                required=True)

    notes = fields.String()
    
    @validates('ribcage_movement')
    def valid_ribcage_movement(self,value):
        for option in value:
            if option not in self.ribcage_movement_test_options:
                raise ValidationError(f'{option} is not a valid movement descriptor. Use one of the following {self.ribcage_movement_test_options}')
            
    @validates('pelvis_movement')
    def valid_pelvis_movement(self,value):
        for option in value:
            if option not in self.pelvis_movement_test_options:
                raise ValidationError(f'{option} is not a valid movement descriptor. Use one of the following {self.pelvis_movement_test_options}')
            

class StandingRotationNotesSchema(Schema):
    notes = fields.String()

class StandingRotationSchema(Schema):
    right = fields.Nested(StandingRotationNotesSchema)
    left = fields.Nested(StandingRotationNotesSchema)

class MovementAssessmentSchema(Schema):
    clientid = fields.Integer(missing=0)
    timestamp = fields.DateTime()
    squat = fields.Nested(SquatTestSchema)
    toe_touch = fields.Nested(ToeTouchTestSchema)
    standing_rotation = fields.Nested(StandingRotationSchema)

    @post_load
    def unravel(self, data, **kwargs):
        flat_data = {'clientid': data['clientid'],
                    'timestamp': datetime.utcnow(),
                    'squat_depth': data['squat']['depth'],
                    'squat_ramp': data['squat']['ramp'],
                    'squat_eye_test': data['squat']['eye_test'],
                    'squat_can_breathe': data['squat']['can_breathe'],
                    'squat_can_look_up': data['squat']['can_look_up'],
                    'toe_touch_depth': data['toe_touch']['depth'],
                    'toe_touch_pelvis_movement': data['toe_touch']['pelvis_movement'],
                    'toe_touch_ribcage_movement': data['toe_touch']['ribcage_movement'],
                    'toe_touch_notes': data['toe_touch']['notes'],
                    'standing_rotation_r_notes': data['standing_rotation']['right']['notes'],
                    'standing_rotation_l_notes': data['standing_rotation']['left']['notes']
        }

        return MovementAssessment(**flat_data)

    @pre_dump
    def ravel(self, data, **kwargs):
        nested = {"clientid": data.clientid,
                  "timestamp": data.timestamp,
                  "squat": {
                      "depth": data.squat_depth ,
                      "ramp": data.squat_ramp,
                      "eye_test": data.squat_eye_test,
                      "can_breathe": data.squat_can_breathe,
                      "can_look_up": data.squat_can_look_up
                  },
                  "toe_touch" : {
                      "depth": data.toe_touch_depth,
                      "pelvis_movement": data.toe_touch_pelvis_movement,
                      "ribcage_movement": data.toe_touch_ribcage_movement,
                      "notes": data.toe_touch_notes
                  },
                  "standing_rotation": {
                      "right": {
                          "notes": data.standing_rotation_r_notes
                      },
                      "left":{
                          "notes": data.standing_rotation_l_notes
                      } 
                  }
        }

        return nested

class HeartAssessmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = HeartAssessment

    clientid = fields.Integer(missing=0)
    vital_heartrate = fields.Float(description="vital_heartrate pulled from doctor physical data", dump_only=True)
    
    @post_load
    def make_object(self, data, **kwargs):
        return HeartAssessment(**data)

    @pre_dump
    def add_vital_heartrate(self, data, **kwargs):
        """Add vital_heartrate from most recent medial physical"""
        data_dict = data.__dict__
        recent_physical = MedicalPhysicalExam.query.filter_by(clientid=data.clientid).order_by(MedicalPhysicalExam.idx.desc()).first()
        data_dict["vital_heartrate"] = recent_physical.vital_heartrate
        return data_dict

        



class MoxyAssessmentSchema(ma.SQLAlchemySchema):
    class Meta:
        model = MoxyAssessment
    
    limiter_list = ['Demand','Supply','Respiratory']
    performance_metric_list = ['Watts','Lbs','Feet/Min']

    clientid = fields.Integer(missing=0)
    timestamp = ma.auto_field()
    notes = ma.auto_field()
    vl_side = fields.String(description="vl_side must be either 'right' or 'left'")
    performance_baseline = fields.Integer(description="", validate=validate.Range(min=0, max=100))
    recovery_baseline = fields.Integer(description="", validate=validate.Range(min=0, max=100))
    gas_tank_size = fields.Integer(description="", validate=validate.Range(min=0, max=100))
    starting_sm_o2 = fields.Integer(description="", validate=validate.Range(min=0, max=100))
    starting_thb = fields.Integer(description="", validate=validate.Range(min=9, max=18))
    limiter = fields.String(description=f"must be one of: {limiter_list}")
    intervention = ma.auto_field()
    performance_metric_1 = fields.String(description=f"must be one of: {performance_metric_list}")
    performance_metric_2 = fields.String(description=f"must be one of: {performance_metric_list}")
    performance_metric_1_value = fields.Integer(description="value in regards to chosen performance metric", validate=validate.Range(min=0, max=1500))
    performance_metric_2_value = fields.Integer(description="value in regards to chosen performance metric", validate=validate.Range(min=0, max=1500))

    @validates('vl_side')
    def validate_vl_side(self,value):
        if value not in ["right", "left"]:
            raise ValidationError(f"{value} not a valid option. must be 'right' or 'left'")
    
    @validates('limiter')
    def limiter_picklist(self,value):
        if not value in self.limiter_list:
            raise ValidationError(f'limiter entry invalid. Please use one of the following: {self.limiter_list}')

    @validates('performance_metric_1')
    def performance_metric_1_picklist(self,value):
        if not value in self.performance_metric_list:
            raise ValidationError(f'performance_metric_1 entry invalid. Please use one of the following: {self.performance_metric_list}')

    @validates('performance_metric_2')
    def performance_metric_2_picklist(self,value):
        if not value in self.performance_metric_list:
            raise ValidationError(f'performance_metric_2 entry invalid. Please use one of the following: {self.performance_metric_list}')

    @post_load
    def make_object(self, data, **kwargs):
        return MoxyAssessment(**data)

class LungAssessmentSchema(ma.SQLAlchemySchema):
    class Meta:
        model = LungAssessment
        
    clientid = fields.Integer(missing=0)
    timestamp = ma.auto_field()
    notes = ma.auto_field()
    vital_weight = fields.Float(description="weight pulled from doctor physical data", dump_only=True)
    bag_size = fields.Float(description="in liters", validate=validate.Range(min=0, max=10))
    duration = fields.Integer(description="in seconds", validate=validate.Range(min=0, max=300))
    breaths_per_minute = fields.Integer(description="", validate=validate.Range(min=0, max=100))
    max_minute_volume = fields.Float(description="", validate=validate.Range(min=0, max=500))
    liters_min_kg = fields.Float(description="liters per minute per kg", validate=validate.Range(min=0, max=100))

    @post_load
    def make_object(self, data, **kwargs):
        return LungAssessment(**data)

    @pre_dump
    def add_weight(self, data, **kwargs):
        "add vital weight to the dump"
        data_dict = data.__dict__
        recent_physical = MedicalPhysicalExam.query.filter_by(clientid=data.clientid).order_by(MedicalPhysicalExam.idx.desc()).first()
        data_dict["vital_weight"] = recent_physical.vital_weight
        return data_dict
    

class MoxyRipExaminationSchema(Schema):

    smo2 = fields.Integer(description="", validate=validate.Range(min=0, max=100))
    thb = fields.Integer(description="", validate=validate.Range(min=9, max=18))
    avg_power = fields.Integer(description="", validate=validate.Range(min=0, max=1500))
    hr_max_min = fields.Integer(description="", validate=validate.Range(min=0, max=220))

class MoxyTries(Schema):
    one = fields.Nested(MoxyRipExaminationSchema)
    two = fields.Nested(MoxyRipExaminationSchema)
    three = fields.Nested(MoxyRipExaminationSchema)
    four = fields.Nested(MoxyRipExaminationSchema)

class MoxyRipSchema(Schema):
    limiter_options = ['Demand','Supply','Respiratory']

    clientid = fields.Integer(missing=0)
    timestamp = fields.DateTime()
    vl_side = fields.String(description="vl_side must be either 'right' or 'left'")
    performance = fields.Nested(MoxyTries)
    recovery = fields.Nested(MoxyTries)
    smo2_tank_size = fields.Integer(description="", validate=validate.Range(min=0, max=100))
    thb_tank_size = fields.Integer(description="", validate=validate.Range(min=9, max=18))
    performance_baseline_smo2 = fields.Integer(description="", validate=validate.Range(min=0, max=100))
    performance_baseline_thb = fields.Integer(description="", validate=validate.Range(min=9, max=18))
    recovery_baseline_smo2 = fields.Integer(description="", validate=validate.Range(min=0, max=100))
    recovery_baseline_thb = fields.Integer(description="", validate=validate.Range(min=9, max=18))
    avg_watt_kg = fields.Float(description="", validate=validate.Range(min=0, max=20))
    avg_interval_time = fields.Integer(description="seconds", validate=validate.Range(min=0, max=360))
    avg_recovery_time = fields.Integer(description="seconds", validate=validate.Range(min=0, max=360))

    limiter = fields.String(description=f"must be one of the following choices: {limiter_options}")

    intervention = fields.String()
    vital_weight = fields.Float(description="weight pulled from doctor physical data", dump_only=True)


    @validates('vl_side')
    def validate_vl_side(self,value):
        if value not in ["right", "left"]:
            raise ValidationError(f"{value} not a valid option. must be 'right' or 'left'")

    @validates('limiter')
    def valid_limiter(self,value):
        if value not in self.limiter_options:
            raise ValidationError(f'{value} is not a valid limiter option. Use one of the following {self.limiter_options}')

    @post_load
    def unravel(self, data, **kwargs):
        flat_data = {'clientid': data['clientid'],
                    'timestamp': datetime.utcnow(),
                    'vl_side': data['vl_side'],
                    'performance_smo2_1':          data['performance']['one']['smo2'],
                    'performance_thb_1':           data['performance']['one']['thb'],
                    'performance_average_power_1': data['performance']['one']['avg_power'],
                    'performance_hr_max_1':        data['performance']['one']['hr_max_min'],
                    'performance_smo2_2':          data['performance']['two']['smo2'],
                    'performance_thb_2':           data['performance']['two']['thb'],
                    'performance_average_power_2': data['performance']['two']['avg_power'],
                    'performance_hr_max_2':        data['performance']['two']['hr_max_min'],
                    'performance_smo2_3':          data['performance']['three']['smo2'],
                    'performance_thb_3':           data['performance']['three']['thb'],
                    'performance_average_power_3': data['performance']['three']['avg_power'],
                    'performance_hr_max_3':        data['performance']['three']['hr_max_min'],
                    'performance_smo2_4':          data['performance']['four']['smo2'],
                    'performance_thb_4':           data['performance']['four']['thb'],
                    'performance_average_power_4': data['performance']['four']['avg_power'],
                    'performance_hr_max_4':        data['performance']['four']['hr_max_min'],
                    'recovery_smo2_1':          data['recovery']['one']['smo2'],
                    'recovery_thb_1':           data['recovery']['one']['thb'],
                    'recovery_average_power_1': data['recovery']['one']['avg_power'],
                    'recovery_hr_min_1':        data['recovery']['one']['hr_max_min'],
                    'recovery_smo2_2':          data['recovery']['two']['smo2'],
                    'recovery_thb_2':           data['recovery']['two']['thb'],
                    'recovery_average_power_2': data['recovery']['two']['avg_power'],
                    'recovery_hr_min_2':        data['recovery']['two']['hr_max_min'],
                    'recovery_smo2_3':          data['recovery']['three']['smo2'],
                    'recovery_thb_3':           data['recovery']['three']['thb'],
                    'recovery_average_power_3': data['recovery']['three']['avg_power'],
                    'recovery_hr_min_3':        data['recovery']['three']['hr_max_min'],
                    'recovery_smo2_4':          data['recovery']['four']['smo2'],
                    'recovery_thb_4':           data['recovery']['four']['thb'],
                    'recovery_average_power_4': data['recovery']['four']['avg_power'],
                    'recovery_hr_min_4':        data['recovery']['four']['hr_max_min'],
                    'smo2_tank_size': data['smo2_tank_size'],
                    'thb_tank_size': data['thb_tank_size'],
                    'performance_baseline_smo2': data['performance_baseline_smo2'],     
                    'performance_baseline_thb': data['performance_baseline_thb'],
                    'recovery_baseline_smo2': data['recovery_baseline_smo2'],
                    'recovery_baseline_thb': data['recovery_baseline_thb'],
                    'avg_watt_kg': data['avg_watt_kg'],
                    'avg_interval_time':data['avg_watt_kg'],
                    'avg_recovery_time': data['avg_recovery_time'],
                    'limiter': data['limiter'],
                    'intervention': data['intervention']
        }
        return MoxyRipTest(**flat_data)

    @pre_dump
    def ravel(self, data, **kwargs):
        nested = {
            "vl_side": data.vl_side,
            "recovery_baseline_smo2": data.recovery_baseline_smo2,
            "performance": {
                "two": {
                    "smo2": data.performance_smo2_2,
                    "avg_power": data.performance_average_power_2,
                    "thb": data.performance_thb_2,
                    "hr_max_min": data.performance_hr_max_2
                },
                "one": {
                    "smo2": data.performance_smo2_1,
                    "avg_power": data.performance_average_power_1,
                    "thb": data.performance_thb_1,
                    "hr_max_min": data.performance_hr_max_1
                },
                "three": {
                    "smo2": data.performance_smo2_3,
                    "avg_power": data.performance_average_power_3,
                    "thb": data.performance_thb_3,
                    "hr_max_min": data.performance_hr_max_3
                },
                "four": {
                    "smo2": data.performance_smo2_4,
                    "avg_power": data.performance_average_power_4,
                    "thb": data.performance_thb_4,
                    "hr_max_min": data.performance_hr_max_4
                }
            },
            "recovery": {
                "two": {
                    "smo2": data.recovery_smo2_2,
                    "avg_power": data.recovery_average_power_2,
                    "thb": data.recovery_thb_2,
                    "hr_max_min": data.recovery_hr_min_2
                },
                "one": {
                    "smo2": data.recovery_smo2_1,
                    "avg_power": data.recovery_average_power_1,
                    "thb": data.recovery_thb_1,
                    "hr_max_min": data.recovery_hr_min_1
                },
                "three": {
                    "smo2": data.recovery_smo2_3,
                    "avg_power": data.recovery_average_power_3,
                    "thb": data.recovery_thb_3,
                    "hr_max_min": data.recovery_hr_min_3
                },
                "four": {
                    "smo2": data.recovery_smo2_4,
                    "avg_power": data.recovery_average_power_4,
                    "thb": data.recovery_thb_4,
                    "hr_max_min": data.recovery_hr_min_4
                }
            },
            "timestamp": data.timestamp,
            "performance_baseline_smo2": data.performance_baseline_smo2,
            "performance_baseline_thb": data.performance_baseline_thb,
            "thb_tank_size": data.thb_tank_size,
            "avg_watt_kg": data.avg_watt_kg,
            "recovery_baseline_thb": data.recovery_baseline_thb,
            "avg_interval_time": data.avg_interval_time,
            "avg_recovery_time": data.avg_recovery_time,
            "clientid": data.clientid,
            "smo2_tank_size": data.smo2_tank_size,
            "limiter": data.limiter,
            "intervention": data.intervention
        }
        # add vital_weight from client's most recent physical examination
        recent_physical = MedicalPhysicalExam.query.filter_by(clientid=data.clientid).order_by(MedicalPhysicalExam.idx.desc()).first()
        nested["vital_weight"] = recent_physical.vital_weight
        return nested


class FitnessQuestionnaireSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = FitnessQuestionnaire
        exclude = ('idx',)
    
    stressors_list = ['Family',	'Work', 'Finances', 'Social Obligations', 'Health', 'Relationships', 'School', 'Body Image',			
                        'Sports Performance', 'General Environment', 'Other']
    physical_goals_list = ['Weight Loss','Increase Strength','Increase Aerobic Capacity','Body Composition','Sport Specific Performance',			
                            'Improve Mobility', 'Injury Rehabilitation', 'Injury Prevention', 'Increase Longevity', 'General Health', 'Other']
    lifestyle_goals_list = ['Increased Energy', 'Increased Mental Clarity', 'Improved Relationships', 'Increased Libido',			
                                'Overall Happiness', 'Decreased Stress', 'Improved Sleep', 'Healthier Eating', 'Other']

    trainer_goals_list = ['Expertise', 'Motivation', 'Accountability', 'Time Efficiency', 'Other']
    sleep_hours_options_list = ['< 4', '4-6','6-8','> 8']
        
    clientid = fields.Integer(missing=0)
    timestamp = fields.DateTime(description="timestamp of questionnaire. Filled by backend")

    stress_sources = fields.List(fields.String,
            description=f"List of sources of stress. Options: {stressors_list}",
            required=True) 
    lifestyle_goals = fields.List(fields.String,
            description=f"List of lifestyle change goals. Limit of three from these options: {lifestyle_goals_list}. If other, must specify",
            required=True) 
    physical_goals = fields.List(fields.String,
            description=f"List of sources of stress. Limit of three from these options: {physical_goals_list}. If other, must specify",
            required=True) 
    trainer_expectation = fields.String(description=f"Client's expectation for their trainer. Must be one of: {trainer_goals_list}")
    sleep_hours = fields.String(description=f"nightly hours of sleep bucketized by the following options: {sleep_hours_options_list}")

    sleep_quality_level = fields.Integer(description="current sleep quality rating 1-5", validate=validate.Range(min=1, max=5))
    stress_level = fields.Integer(description="current stress rating 1-5", validate=validate.Range(min=1, max=5))
    energy_level = fields.Integer(description="current energy rating 1-5", validate=validate.Range(min=1, max=5))
    libido_level = fields.Integer(description="current libido rating 1-5", validate=validate.Range(min=1, max=5))
    confidence_level = fields.Integer(description="current confidence rating 1-5", validate=validate.Range(min=1, max=5))

    current_fitness_level = fields.Integer(description="current fitness level 1-10", validate=validate.Range(min=1, max=10))
    goal_fitness_level = fields.Integer(description="foal fitness level 1-10", validate=validate.Range(min=1, max=10))
    
    
    @post_load
    def make_object(self, data, **kwargs):
        return FitnessQuestionnaire(**data)

    @validates('stress_sources')
    def validate_stress_sources(self,value):
        for item in value:
            if item not in self.stressors_list:
                raise ValidationError(f"{item} not a valid option. must be in {self.stressors_list}")

    @validates('lifestyle_goals')
    def validate_lifestyle_goals(self,value):
        for item in value:
            if item not in self.lifestyle_goals_list:
                raise ValidationError(f"{item} not a valid option. must be in {self.lifestyle_goals_list}")
        if len(value) > 3:
            ValidationError("limit list length to 3 choices")


    @validates('physical_goals')
    def validate_physical_goals(self,value):
        for item in value:
            if item not in self.physical_goals_list:
                raise ValidationError(f"{item} not a valid option. must be in {self.physical_goals_list}")
        if len(value) > 3:
            ValidationError("limit list length to 3 choices")
    
    @validates('trainer_expectation')
    def validate_trainer_expectations(self, value):
        if value not in self.trainer_goals_list:
            raise ValidationError(f"{value} not a valid option. Must be one of {self.trainer_goals_list}")

    @validates('sleep_hours')
    def validate_sleep_hours(self, value):
        if value not in self.sleep_hours_options_list:
            raise ValidationError(f"{value} not a valid option. Must be one of {self.sleep_hours_options_list}")


"""
    Schemas for the doctor's API
"""
class MedicalImagingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MedicalImaging
        load_instance = True
        exclude = ["clientid", "idx"]

    possible_image_types = ['CT scan', 'MRI', 'PET scan', 'Ultrasound', 'X-Ray']
    image_type = fields.String(validate=validate.OneOf(possible_image_types), required=True)

    #
    """clientid = fields.Integer(missing=0)
    possible_image_types = ['CT scan', 'MRI', 'PET scan', 'Ultrasound', 'X-Ray']
    image_date = fields.DateTime(format='%Y-%m-%d', required=True)
    image_read = fields.String(required=True)
    image_type = fields.String(validate=validate.OneOf(possible_image_types), required=True)
    files = fields.Dict()
    image_name = fields.String()
    image_origin_location = fields.String()
    image_cpt_code = fields.String()
    
    
    @post_load
    def make_object(self, data, **kwargs):
        return MedicalImaging(**data)   """


class BloodChemistryCBCSchema(Schema):

    # Validate each payload entry
    idx = fields.Integer(required=False)
    clientid = fields.Integer(missing=0)
    exam_date = fields.DateTime(format='%Y-%m-%d')
    rbc = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    hemoglobin = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    hematocrit = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    mcv = fields.Float(description="",validate=validate.Range(min=0, max=200),required=True)
    mch = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    mchc = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    rdw = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    wbc = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    rel_neutrophils = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    abs_neutrophils = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    rel_lymphocytes = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    abs_lymphocytes = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    rel_monocytes = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    abs_monocytes = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    rel_eosinophils = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    abs_eosinophils = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    basophils = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    platelets = fields.Float(description="",validate=validate.Range(min=0, max=500),required=True)

    plateletsByMch = fields.Float()
    plateletsByLymphocyte = fields.Float()
    neutrophilByLymphocyte = fields.Float()
    lymphocyteByMonocyte = fields.Float()

    @post_load
    def make_object(self, data, **kwargs):
        return MedicalBloodChemistryCBC(**data)

class BloodChemistryCMPSchema(Schema):

    # Validate each payload entry
    idx = fields.Integer(required=False)
    clientid = fields.Integer(missing=0)
    exam_date = fields.DateTime(format='%Y-%m-%d')
    glucose = fields.Float(description="",validate=validate.Range(min=0, max=200),required=True)
    sodium = fields.Float(description="",validate=validate.Range(min=0, max=500),required=True)
    potassium = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    carbon_dioxide = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    chloride = fields.Float(description="",validate=validate.Range(min=0, max=500),required=True)
    magnesium = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    calcium = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    phosphorus = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    uric_acid = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    bun = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    creatinine = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    ast = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    alt = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    alk_phophatase = fields.Float(description="",validate=validate.Range(min=0, max=200),required=True)
    bilirubin = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    protein = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    albumin = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)
    globulin = fields.Float(description="",validate=validate.Range(min=0, max=100),required=True)

    bunByAlbumin = fields.Float()

    @post_load
    def make_object(self, data, **kwargs):
        return MedicalBloodChemistryCMP(**data)


class MedicalHistorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MedicalHistory
        
    clientid = fields.Integer(missing=0)
    
    @post_load
    def make_object(self, data, **kwargs):
        return MedicalHistory(**data)
    
class MedicalPhysicalExamSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MedicalPhysicalExam
        
    clientid = fields.Integer(missing=0)
    vital_height = fields.String(description="Deprecated, use vital_height_inches instead", missing="")
    
    @post_load
    def make_object(self, data, **kwargs):
        return MedicalPhysicalExam(**data)


class MedicalInstitutionsSchema(ma.SQLAlchemyAutoSchema):
    """
    For returning medical institutions in GET request and also accepting new institute names
    """
    class Meta:
        model = MedicalInstitutions

    @post_load
    def make_object(self, data):
        return MedicalInstitutions(**data)

class ClientExternalMRSchema(Schema):
    """
    For returning medical institutions in GET request and also accepting new institute names
    """

    clientid = fields.Integer(missing=0)
    institute_id = fields.Integer(missing=9999)
    med_record_id = fields.String()
    institute_name = fields.String(load_only=True, required=False, missing="")

    @post_load
    def make_object(self, data, **kwargs):
        data.pop("institute_name")
        return ClientExternalMR(**data)

class ClientExternalMREntrySchema(Schema):
    """
    For returning medical institutions in GET request and also accepting new institute names
    """

    record_locators = fields.Nested(ClientExternalMRSchema, many=True)
    
    @pre_dump
    def ravel(self, data, **kwargs):
        """upon dump, add back the schema structure"""
        response = {"record_locators": data}
        return response

"""
    Schemas for the staff API
"""
class StaffSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Staff

    possible_roles = ['stfappadmin', 'clntsvc', 'physthera', 'phystrain', 'datasci', 'doctor', 'docext', 'nutrition']

    token = fields.String(dump_only=True)
    token_expiration = fields.DateTime(dump_only=True)
    password = fields.String(required=True, load_only=True)
    email = fields.Email(required=True)
    access_roles = fields.List(fields.String,
                description=" The access role for this staff member options: \
                ['stfappadmin' (staff application admin), 'clntsvc' (client services), 'physthera' (physiotherapist), 'datasci' (data scientist), 'doctor' (doctor), 'docext' (external doctor), 'phystrain' (physical trainer),\
                 'nutrition' (nutritionist)]",
                required=True)
    is_system_admin = fields.Boolean(dump_only=True, missing=False)
    is_admin = fields.Boolean(dump_only=True, missing=False)
    staffid = fields.Integer(dump_only=True)

    @validates('access_roles')
    def valid_access_roles(self,value):
        for role in value:
            if role not in self.possible_roles:
                raise ValidationError(f'{role} is not a valid access role. Use one of the following {self.possible_roles}')
            
    @post_load
    def make_object(self, data, **kwargs):
        new_staff = Staff(**data)
        new_staff.set_password(data['password'])
        return new_staff


class MedicalBloodChemistryThyroidSchema(Schema):
        
    idx = fields.Integer()
    clientid = fields.Integer(missing=0)
    exam_date = fields.Date()
    t3_resin_uptake = fields.Integer(validate=validate.Range(min=25,max=35))
    thyroglobulin = fields.Integer(validate=validate.Range(min=0,max=20))
    thyroidial_iodine_uptake = fields.Integer(validate=validate.Range(min=5,max=30))
    tsh = fields.Float(validate=validate.Range(min=0.5,max=4.0))
    tsi = fields.Integer(validate=validate.Range(min=0,max=130))
    thyroxine_binding_globulin = fields.Integer(validate=validate.Range(min=12,max=27))
    thyroxine_index = fields.Integer(validate=validate.Range(min=5,max=12))
    t4_serum_total = fields.Integer(validate=validate.Range(min=5,max=12))
    t4_serum_free = fields.Float(validate=validate.Range(min=0.8,max=1.8))
    t3_serum_total = fields.Integer(validate=validate.Range(min=80,max=180))
    t3_serum_reverse = fields.Integer(validate=validate.Range(min=20,max=40))
    t3_serum_free = fields.Float(validate=validate.Range(min=2.3,max=4.2))
    
    @post_load
    def make_object(self, data, **kwargs):
        return MedicalBloodChemistryThyroid(**data)


#
#   Schemas for the wearables API
#
class WearablesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Wearables

    clientid = fields.Integer(missing=0)

    @post_load
    def make_object(self, data, **kwargs):
        return Wearables(**data)


class WearablesOuraSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WearablesOura

    clientid = fields.Integer(missing=0)

    @post_load
    def make_object(self, data, **kwargs):
        return WearablesOura(**data)
