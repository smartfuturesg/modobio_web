from datetime import datetime
from hashlib import md5
from marshmallow import Schema, fields, post_load, ValidationError, validates, validate
from marshmallow import post_load, post_dump, pre_dump, pre_load

from odyssey import ma
from .models import ( 
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

"""
    Schemas for the doctor's API
"""
class MedicalImagingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MedicalImaging
        load_instance = True
        exclude = ["clientid", "idx"]

    possible_image_types = ['CT', 'MRI', 'PET', 'Scopes', 'Special imaging', 'Ultrasound', 'X-ray']
    image_type = fields.String(validate=validate.OneOf(possible_image_types), required=True)
    image_date = fields.Date(required=True)
    image_read = fields.String(required=True)
    
class MedicalBloodTestSchema(Schema):
    testid = fields.Integer()
    clientid = fields.Integer(load_only=True)
    date = fields.Date(required=True, format="iso")
    panel_type = fields.String(required=False)
    notes = fields.String(required=False)

    @post_load
    def make_object(self, data, **kwargs):
        return MedicalBloodTests(**data)

class AllMedicalBloodTestSchema(Schema):
    """
    For returning several blood test instance details 
    No actual results are returned, just details on
    the test entry (notes, date, panel_type)
    """
    items = fields.Nested(MedicalBloodTestSchema(many=True))
    total = fields.Integer()
    clientid = fields.Integer()

class MedicalBloodTestResultsSchema(Schema):
    result_name = fields.String()
    result_value = fields.Float()
    evaluation = fields.String(dump_only=True)

class MedicalBloodTestsInputSchema(Schema):
    clientid = fields.Integer()
    date = fields.Date()
    panel_type = fields.String()
    notes = fields.String()
    results = fields.Nested(MedicalBloodTestResultsSchema, many=True)

class BloodTestsByTestID(Schema):
    """
    Organizes blood test results into a nested results field
    General information about the test entry like testid, date, notes, panel
    are in the outer most part of this schema.
    """
    testid = fields.Integer()
    results = fields.Nested(MedicalBloodTestResultsSchema(many=True))
    notes = fields.String()
    panel = fields.String()
    date = fields.Date(format="iso")

class MedicalBloodTestResultsOutputSchema(Schema):
    """
    Schema for outputting a nested json 
    of blood test results. 
    """
    tests = fields.Integer(description="# of test entry sessions. All each test may have more than one test result")
    test_results = fields.Integer(description="# of test results")
    items = fields.Nested(BloodTestsByTestID(many=True), missing = [])
    clientid = fields.Integer()

class MedicalBloodTestResultsSchema(Schema):
    idx = fields.Integer()
    testid = fields.Integer()
    resultid = fields.Integer()
    result_value = fields.Float()

    @post_load
    def make_object(self, data, **kwargs):
        return MedicalBloodTestResults(**data)


class MedicalBloodTestTypes(ma.SQLAlchemyAutoSchema):
    class Meta():
        model = MedicalBloodTestResultTypes
        exclude = ('created_at', 'resultid')

class MedicalBloodTestResultTypesSchema(Schema):
    
    items = fields.Nested(MedicalBloodTestTypes(many=True)) 
    total = fields.Integer()
    
    @post_load
    def make_object(self, data, **kwargs):
        return MedicalBloodTestResultTypes(**data)

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