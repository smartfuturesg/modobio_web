from datetime import datetime
from hashlib import md5
from marshmallow import Schema, fields, post_load, ValidationError, validates, validate
from marshmallow import post_load, post_dump, pre_dump, pre_load

from odyssey import ma
from odyssey.doctor.models import ( 
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
from odyssey.pt.models import Chessboard, PTHistory
from odyssey.staff.models import Staff
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

"""
    Schemas for the trainer's API
"""

class PowerAttemptsPushPull(Schema):
    weight = fields.Integer(description="weight of exercise in PSI", validate=validate.Range(min=0, max=60), missing=None)
    attempt_1 = fields.Integer(description="", validate=validate.Range(min=0, max=4000), missing=None)
    attempt_2 = fields.Integer(description="", validate=validate.Range(min=0, max=4000), missing=None)
    attempt_3 = fields.Integer(description="",validate=validate.Range(min=0, max=4000), missing=None)
    average = fields.Float(description="",validate=validate.Range(min=0, max=4000), missing=None)

class PowerAttemptsLegPress(Schema):
    weight = fields.Integer(description="weight of exercise in PSI", validate=validate.Range(min=0, max=1500),missing=None)
    attempt_1 = fields.Integer(description="", validate=validate.Range(min=0, max=9999),missing=None)
    attempt_2 = fields.Integer(description="", validate=validate.Range(min=0, max=9999),missing=None)
    attempt_3 = fields.Integer(description="",validate=validate.Range(min=0, max=9999),missing=None)
    average = fields.Float(description="",validate=validate.Range(min=0, max=9999),missing=None)

class PowerPushPull(Schema):
    left = fields.Nested(PowerAttemptsPushPull, missing=PowerAttemptsPushPull().load({}))
    right = fields.Nested(PowerAttemptsPushPull, missing=PowerAttemptsPushPull().load({}))

class PowerLegPress(Schema):
    left = fields.Nested(PowerAttemptsLegPress, missing=PowerAttemptsLegPress().load({}))
    right = fields.Nested(PowerAttemptsLegPress, missing=PowerAttemptsLegPress().load({}))
    bilateral = fields.Nested(PowerAttemptsLegPress, missing=PowerAttemptsLegPress().load({}))

class PowerAssessmentSchema(Schema):
    clientid = fields.Integer(missing=0)
    timestamp = fields.DateTime()
    push_pull = fields.Nested(PowerPushPull, missing=PowerPushPull().load({}))
    leg_press = fields.Nested(PowerLegPress, missing=PowerLegPress().load({}))
    upper_watts_per_kg = fields.Float(description = "watts per kg upper body", validate=validate.Range(min=0, max=120), missing=None)
    lower_watts_per_kg = fields.Float(description = "watts per kg lower body", validate=validate.Range(min=0, max=300), missing=None)
    vital_weight = fields.Float(description="weight pulled from doctor physical data", dump_only=True)

    @post_load
    def unravel(self, data, **kwargs):
        flat_data = {'clientid': data['clientid'],
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
                                         'average':   list_average([data.keiser_upper_l_attempt_1,
                                                                       data.keiser_upper_l_attempt_2,
                                                                       data.keiser_upper_l_attempt_3
                                                                    ])
                                        },
                                'right': {'weight':   data.keiser_upper_r_weight,
                                         'attempt_1': data.keiser_upper_r_attempt_1,
                                         'attempt_2': data.keiser_upper_r_attempt_2,
                                         'attempt_3': data.keiser_upper_r_attempt_3,
                                         'average':   list_average([data.keiser_upper_r_attempt_1,
                                                                       data.keiser_upper_r_attempt_2,
                                                                       data.keiser_upper_r_attempt_3
                                                                    ])
                                        },
                                },
                    'leg_press': {'right' : {'weight':   data.keiser_lower_r_weight,
                                             'attempt_1': data.keiser_lower_r_attempt_1,
                                             'attempt_2': data.keiser_lower_r_attempt_2,
                                             'attempt_3': data.keiser_lower_r_attempt_3,
                                             'average':   list_average([data.keiser_lower_r_attempt_1,
                                                                           data.keiser_lower_r_attempt_2,
                                                                           data.keiser_lower_r_attempt_3
                                                                        ])
                                            },
                                  'left': {'weight':   data.keiser_lower_l_weight,
                                             'attempt_1': data.keiser_lower_l_attempt_1,
                                             'attempt_2': data.keiser_lower_l_attempt_2,
                                             'attempt_3': data.keiser_lower_l_attempt_3,
                                             'average':   list_average([data.keiser_lower_l_attempt_1,
                                                                           data.keiser_lower_l_attempt_2,
                                                                           data.keiser_lower_l_attempt_3
                                                                        ])
                                            },
                                  'bilateral': {'weight':   data.keiser_lower_bi_weight,
                                             'attempt_1': data.keiser_lower_bi_attempt_1,
                                             'attempt_2': data.keiser_lower_bi_attempt_2,
                                             'attempt_3': data.keiser_lower_bi_attempt_3,
                                             'average':   list_average([data.keiser_lower_bi_attempt_1,
                                                                           data.keiser_lower_bi_attempt_2,
                                                                           data.keiser_lower_bi_attempt_3
                                                                        ])
                                                }
                                 }
            
                 }
        # add client's vital_weight from most recent physical exam
        recent_physical = MedicalPhysicalExam.query.filter_by(clientid=data.clientid).order_by(MedicalPhysicalExam.idx.desc()).first()
        if not recent_physical:
            nested["vital_weight"] = None
        else:    
            nested["vital_weight"] = recent_physical.vital_weight
        return nested


class StrengthAttemptsPushPull(Schema):
    weight = fields.Integer(description="weight of exercise in PSI", validate=validate.Range(min=0, max=350), missing=None)
    attempt_1 = fields.Integer(description="", validate=validate.Range(min=0, max=50), missing=None)
    attempt_2 = fields.Integer(description="", validate=validate.Range(min=0, max=50), missing=None)
    attempt_3 = fields.Integer(description="",validate=validate.Range(min=0, max=50), missing=None)
    estimated_10rm = fields.Float(description="",validate=validate.Range(min=0, max=350), missing=None)

class StrengthPushPull(Schema):
    notes = fields.String(missing=None)
    left = fields.Nested(StrengthAttemptsPushPull, missing=StrengthAttemptsPushPull().load({}))
    right = fields.Nested(StrengthAttemptsPushPull, missing=StrengthAttemptsPushPull().load({}))
    bilateral = fields.Nested(StrengthAttemptsPushPull, missing=StrengthAttemptsPushPull().load({}))

class StrenghtAssessmentSchema(Schema):
    clientid = fields.Integer(missing=0)
    timestamp = fields.DateTime()
    upper_push = fields.Nested(StrengthPushPull, missing=StrengthPushPull().load({}))
    upper_pull = fields.Nested(StrengthPushPull, missing=StrengthPushPull().load({}))

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
    depth = fields.String(missing=None)
    ramp = fields.String(missing=None)
    eye_test = fields.Boolean(missing=None)
    can_breathe = fields.Boolean(missing=None)
    can_look_up = fields.Boolean(missing=None)

class ToeTouchTestSchema(Schema):
    pelvis_movement_test_options = ['Right Hip High','Right Hip Back','Left Hip High',
                                'Left Hip Back','Right Hip High', 'Even Bilaterally']

    ribcage_movement_test_options = ['Right Posterior Ribcage High','Right Posterior Ribcage Back',	
                                'Left Posterior Ribcage High', 'Left Posterior Ribcage Back', 'Even Bilaterally']
    depth = fields.String(missing=None)
    pelvis_movement = fields.List(fields.String,
                description=f"Descriptors for this assessment must be in the following picklist: {pelvis_movement_test_options}",
                missing=[None]) 
    ribcage_movement = fields.List(fields.String,
                description=f"Descriptors for this assessment must be in the following picklist: {ribcage_movement_test_options}",
                missing=[None])

    notes = fields.String(missing=None)
    
    @validates('ribcage_movement')
    def valid_ribcage_movement(self,value):
        for option in value:
            if option not in self.ribcage_movement_test_options and option != None:
                raise ValidationError(f'{option} is not a valid movement descriptor. Use one of the following {self.ribcage_movement_test_options}')
            
    @validates('pelvis_movement')
    def valid_pelvis_movement(self,value):
        for option in value:
            if option not in self.pelvis_movement_test_options and option != None:
                raise ValidationError(f'{option} is not a valid movement descriptor. Use one of the following {self.pelvis_movement_test_options}')
            

class StandingRotationNotesSchema(Schema):
    notes = fields.String(missing=None)

class StandingRotationSchema(Schema):
    right = fields.Nested(StandingRotationNotesSchema, missing=StandingRotationNotesSchema().load({}))
    left = fields.Nested(StandingRotationNotesSchema, missing=StandingRotationNotesSchema().load({}))

class MovementAssessmentSchema(Schema):
    clientid = fields.Integer(missing=0)
    timestamp = fields.DateTime()
    squat = fields.Nested(SquatTestSchema,missing=SquatTestSchema().load({}))
    toe_touch = fields.Nested(ToeTouchTestSchema, missing=ToeTouchTestSchema().load({}))
    standing_rotation = fields.Nested(StandingRotationSchema, missing=StandingRotationSchema().load({}))

    @post_load
    def unravel(self, data, **kwargs):
        flat_data = {'clientid': data['clientid'],
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
        if not recent_physical:
            data_dict["vital_heartrate"] = None
        else:    
            data_dict["vital_heartrate"] = recent_physical.vital_heartrate
        return data_dict

class MoxyAssessmentSchema(ma.SQLAlchemySchema):
    class Meta:
        model = MoxyAssessment
    
    limiter_list = ['Demand','Supply','Respiratory']
    performance_metric_list = ['Watts','Lbs','Feet/Min']

    clientid = fields.Integer(missing=0)
    timestamp = ma.auto_field()
    notes = ma.auto_field(missing=None)
    vl_side = fields.String(description="vl_side must be either 'right' or 'left'", missing=None)
    performance_baseline = fields.Integer(description="", validate=validate.Range(min=0, max=100), missing=None)
    recovery_baseline = fields.Integer(description="", validate=validate.Range(min=0, max=100), missing=None)
    gas_tank_size = fields.Integer(description="", validate=validate.Range(min=0, max=100), missing=None)
    starting_sm_o2 = fields.Integer(description="", validate=validate.Range(min=0, max=100), missing=None)
    starting_thb = fields.Float(description="", validate=validate.Range(min=9, max=18), missing=None)
    limiter = fields.String(description=f"must be one of: {limiter_list}", missing=None)
    intervention = ma.auto_field(missing=None)
    performance_metric_1 = fields.String(description=f"must be one of: {performance_metric_list}", missing=None)
    performance_metric_2 = fields.String(description=f"must be one of: {performance_metric_list}", missing=None)
    performance_metric_1_value = fields.Integer(description="value in regards to chosen performance metric", validate=validate.Range(min=0, max=1500), missing=None)
    performance_metric_2_value = fields.Integer(description="value in regards to chosen performance metric", validate=validate.Range(min=0, max=1500), missing=None)

    @validates('vl_side')
    def validate_vl_side(self,value):
        if value not in ["right", "left"] and value != None:
            raise ValidationError(f"{value} not a valid option. must be 'right' or 'left'")
    
    @validates('limiter')
    def limiter_picklist(self,value):
        if not value in self.limiter_list and value != None:
            raise ValidationError(f'limiter entry invalid. Please use one of the following: {self.limiter_list}')

    @validates('performance_metric_1')
    def performance_metric_1_picklist(self,value):
        if not value in self.performance_metric_list and value != None:
            raise ValidationError(f'performance_metric_1 entry invalid. Please use one of the following: {self.performance_metric_list}')

    @validates('performance_metric_2')
    def performance_metric_2_picklist(self,value):
        if not value in self.performance_metric_list and value != None:
            raise ValidationError(f'performance_metric_2 entry invalid. Please use one of the following: {self.performance_metric_list}')

    @post_load
    def make_object(self, data, **kwargs):
        return MoxyAssessment(**data)

class LungAssessmentSchema(ma.SQLAlchemySchema):
    class Meta:
        model = LungAssessment
        
    clientid = fields.Integer(missing=0)
    timestamp = ma.auto_field()
    notes = ma.auto_field(missing=None)
    vital_weight = fields.Float(description="weight pulled from doctor physical data", dump_only=True, missing=None)
    bag_size = fields.Float(description="in liters", validate=validate.Range(min=0, max=12), missing=None)
    duration = fields.Integer(description="in seconds", validate=validate.Range(min=0, max=400), missing=None)
    breaths_per_minute = fields.Integer(description="", validate=validate.Range(min=0, max=120), missing=None)
    max_minute_volume = fields.Float(description="", validate=validate.Range(min=0, max=600), missing=None)
    liters_min_kg = fields.Float(description="liters per minute per kg", validate=validate.Range(min=0, max=110), missing=None)

    @post_load
    def make_object(self, data, **kwargs):
        return LungAssessment(**data)

    @pre_dump
    def add_weight(self, data, **kwargs):
        "add vital weight to the dump"
        data_dict = data.__dict__
        recent_physical = MedicalPhysicalExam.query.filter_by(clientid=data.clientid).order_by(MedicalPhysicalExam.idx.desc()).first()
        if not recent_physical:
            data_dict["vital_weight"] = None
        else:    
            data_dict["vital_weight"] = recent_physical.vital_weight
        return data_dict
    

class MoxyRipExaminationSchema(Schema):

    smo2 = fields.Integer(description="", validate=validate.Range(min=0, max=100), missing=None)
    thb = fields.Float(description="", validate=validate.Range(min=9, max=18), missing=None)
    avg_power = fields.Integer(description="", validate=validate.Range(min=0, max=1800), missing=None)
    hr_max_min = fields.Integer(description="", validate=validate.Range(min=0, max=220), missing=None)

class MoxyTries(Schema):
    one = fields.Nested(MoxyRipExaminationSchema, missing = MoxyRipExaminationSchema().load({}))
    two = fields.Nested(MoxyRipExaminationSchema, missing = MoxyRipExaminationSchema().load({}))
    three = fields.Nested(MoxyRipExaminationSchema, missing = MoxyRipExaminationSchema().load({}))
    four = fields.Nested(MoxyRipExaminationSchema, missing = MoxyRipExaminationSchema().load({}))

class MoxyRipSchema(Schema):
    limiter_options = ['Demand','Supply','Respiratory']

    clientid = fields.Integer(missing=0)
    timestamp = fields.DateTime()
    vl_side = fields.String(description="vl_side must be either 'right' or 'left'", missing=None)
    performance = fields.Nested(MoxyTries, missing=MoxyTries().load({}))
    recovery = fields.Nested(MoxyTries, missing=MoxyTries().load({}))
    smo2_tank_size = fields.Integer(description="", validate=validate.Range(min=0, max=110), missing=None)
    thb_tank_size = fields.Float(description="", validate=validate.Range(min=9, max=18), missing=None)
    performance_baseline_smo2 = fields.Integer(description="", validate=validate.Range(min=0, max=110), missing=None)
    performance_baseline_thb = fields.Float(description="", validate=validate.Range(min=9, max=18), missing=None)
    recovery_baseline_smo2 = fields.Integer(description="", validate=validate.Range(min=0, max=110), missing=None)
    recovery_baseline_thb = fields.Float(description="", validate=validate.Range(min=9, max=18), missing=None)
    avg_watt_kg = fields.Float(description="", validate=validate.Range(min=0, max=60), missing=None)
    avg_interval_time = fields.Integer(description="seconds", validate=validate.Range(min=0, max=400), missing=None)
    avg_recovery_time = fields.Integer(description="seconds", validate=validate.Range(min=0, max=400), missing=None)

    limiter = fields.String(description=f"must be one of the following choices: {limiter_options}", missing=None)

    intervention = fields.String(missing=None)
    vital_weight = fields.Float(description="weight pulled from doctor physical data", dump_only=True, missing=None)


    @validates('vl_side')
    def validate_vl_side(self,value):
        if value not in ["right", "left"] and value!= None:
            raise ValidationError(f"{value} not a valid option. must be 'right' or 'left'")

    @validates('limiter')
    def valid_limiter(self,value):
        if value not in self.limiter_options and value != None:
            raise ValidationError(f'{value} is not a valid limiter option. Use one of the following {self.limiter_options}')

    @post_load
    def unravel(self, data, **kwargs):
        flat_data = {'clientid': data['clientid'],
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
        if not recent_physical:
            nested["vital_weight"] = None
        else:    
            nested["vital_weight"] = recent_physical.vital_weight
        return nested


class FitnessQuestionnaireSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = FitnessQuestionnaire
        exclude = ('idx','created_at', 'updated_at')
    
    stressors_list = ['Family',	'Work',
                      'Finances', 'Social Obligations',
                      'Health', 'Relationships',
                      'School', 'Body Image',			
                      'Sports Performance',
                      'General Environment',
                      ]
    physical_goals_list = ['Weight Loss','Increase Strength',
                           'Increase Aerobic Capacity','Body Composition',
                           'Sport Specific Performance', 'Improve Mobility',
                           'Injury Rehabilitation', 'Injury Prevention',
                           'Increase Longevity', 'General Health',
                           ]
    lifestyle_goals_list = ['Increased Energy', 'Increased Mental Clarity', 
                            'Increased Libido', 'Overall Happiness', 
                            'Decreased Stress', 'Improved Sleep', 
                            'Healthier Eating', ]

    trainer_goals_list = ['Expertise', 'Motivation', 'Accountability', 'Time Efficiency']
    sleep_hours_options_list = ['< 4', '4-6','6-8','> 8']
        
    clientid = fields.Integer(missing=0)
    timestamp = fields.DateTime(description="timestamp of questionnaire. Filled by backend")
    physical_goals = fields.List(fields.String,
            description=f"List of sources of stress. Limit of three from these options: {physical_goals_list}. If other, must specify",
            missing=[None]) 
    current_fitness_level = fields.Integer(description="current fitness level 1-10", validate=validate.Range(min=1, max=10), missing=None)
    goal_fitness_level = fields.Integer(description="goal fitness level 1-10", validate=validate.Range(min=1, max=10), missing=None)
    trainer_expectations = fields.List(fields.String,
        description=f"Client's expectation for their trainer. Choice of: {trainer_goals_list}", 
        missing=[None])
    sleep_hours = fields.String(description=f"nightly hours of sleep bucketized by the following options: {sleep_hours_options_list}", missing=None)
    sleep_quality_level = fields.Integer(description="current sleep quality rating 1-10", validate=validate.Range(min=1, max=10), missing=None)
    stress_level = fields.Integer(description="current stress rating 1-10", validate=validate.Range(min=1, max=10), missing=None)
    stress_sources = fields.List(fields.String,
            description=f"List of sources of stress. Options: {stressors_list}",
            missing=[None]) 

    lifestyle_goals = fields.List(fields.String,
            description=f"List of lifestyle change goals. Limit of three from these options: {lifestyle_goals_list}. If other, must specify",
            missing=[None]) 
    physical_goals = fields.List(fields.String,
            description=f"List of sources of stress. Limit of three from these options: {physical_goals_list}. If other, must specify",
            missing=[None]) 

    energy_level = fields.Integer(description="current energy rating 1-10", validate=validate.Range(min=1, max=10), missing=None)
    libido_level = fields.Integer(description="current libido rating 1-10", validate=validate.Range(min=1, max=10), missing=None)
    
    @post_load
    def make_object(self, data, **kwargs):
        return FitnessQuestionnaire(**data)

    @validates('stress_sources')
    def validate_stress_sources(self,value):
        for item in value:
            if item not in self.stressors_list and item != None:
                raise ValidationError(f"{item} not a valid option. must be in {self.stressors_list}")

    @validates('lifestyle_goals')
    def validate_lifestyle_goals(self,value):
        for item in value:
            if item not in self.lifestyle_goals_list and item != None:
                raise ValidationError(f"{item} not a valid option. must be in {self.lifestyle_goals_list}")
        if len(value) > 3:
            ValidationError("limit list length to 3 choices")


    @validates('physical_goals')
    def validate_physical_goals(self,value):
        for item in value:
            if item not in self.physical_goals_list and item != None:
                raise ValidationError(f"{item} not a valid option. must be in {self.physical_goals_list}")
        if len(value) > 3:
            ValidationError("limit list length to 3 choices")
    
    @validates('trainer_expectations')
    def validate_trainer_expectationss(self, value):
        for item in value:
            if item not in self.trainer_goals_list and item != None:
                raise ValidationError(f"{item} not a valid option. must be in {self.trainer_goals_list}")

    @validates('sleep_hours')
    def validate_sleep_hours(self, value):
        if value not in self.sleep_hours_options_list and value != None:
            raise ValidationError(f"{value} not a valid option. Must be one of {self.sleep_hours_options_list}")

