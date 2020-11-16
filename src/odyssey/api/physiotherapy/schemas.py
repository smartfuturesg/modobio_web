from datetime import datetime
from marshmallow import (
    Schema, 
    fields, 
    post_load, 
    ValidationError, 
    validates, 
    validate,
    pre_dump
)
from odyssey import ma
from odyssey.api.user.models import User
from odyssey.api.physiotherapy.models import Chessboard, PTHistory

"""
    Schemas for the pt (physical therapy) API
"""

class PTHistorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PTHistory
        
    user_id = fields.Integer(missing=0)
    
    @post_load
    def make_object(self, data, **kwargs):
        return PTHistory(**data)



class ShoulderRotationSchema(Schema):
    ir = fields.Integer(description="internal rotation", validate=validate.Range(min=0, max=110), missing=None)
    er = fields.Integer(description="external rotation", validate=validate.Range(min=0, max=130), missing=None)
    abd = fields.Integer(description="abduction", validate=validate.Range(min=0, max=90), missing=None)
    add = fields.Integer(description="adduction", validate=validate.Range(min=0, max=150), missing=None)
    flexion  = fields.Integer(validate=validate.Range(min=0, max=190), missing=None)
    extension  = fields.Integer(validate=validate.Range(min=0, max=90), missing=None)

class HipRotationSchema(Schema):
    ir = fields.Integer(description="internal rotation", validate=validate.Range(min=-20, max=100), missing=None)
    er = fields.Integer(description="external rotation", validate=validate.Range(min=-20, max=100), missing=None)
    abd = fields.Integer(description="abduction", validate=validate.Range(min=0, max=90), missing=None)
    add = fields.Integer(description="adduction",validate=validate.Range(min=0, max=60), missing=None)
    flexion  = fields.Integer(validate=validate.Range(min=0, max=180), missing=None)
    extension  = fields.Integer(validate=validate.Range(min=0, max=120), missing=None)
    slr  = fields.Integer(validate=validate.Range(min=0, max=180), missing=None)

class ChessBoardShoulderSchema(Schema):
    left = fields.Nested(ShoulderRotationSchema, missing = ShoulderRotationSchema().load({}))
    right = fields.Nested(ShoulderRotationSchema, missing = ShoulderRotationSchema().load({}))

class ChessBoardHipSchema(Schema):
    left = fields.Nested(HipRotationSchema, missing = HipRotationSchema().load({}))
    right = fields.Nested(HipRotationSchema, missing = HipRotationSchema().load({}))

class ChessboardSchema(Schema):
    isa_structure_list  = ['Inhaled','Exhaled', 'Asymmetrical Normal','Asymmetrical Atypical']
    isa_movement_list  = ['Dynamic', 'Static', 'R Static/Left Dynamic', 'L Static/Right Dynamic']

    user_id = fields.Integer(missing=0)
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
        flat_data = {'user_id': data['user_id'],
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
        nested = {'user_id': data.user_id,
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

