from marshmallow import Schema, fields, post_load, validate, pre_dump

from odyssey import ma
from odyssey.api.doctor.models import ( 
    MedicalFamilyHistory,
    MedicalConditions,
    MedicalHistory,
    MedicalPhysicalExam,
    MedicalImaging,
    MedicalBloodTests,
    MedicalBloodTestResults,
    MedicalBloodTestResultTypes
)
from odyssey.api.user.models import User
from odyssey.api.client.models import ClientExternalMR
from odyssey.api.facility.models import MedicalInstitutions

"""
    Schemas for the doctor's API
"""

class MedicalConditionsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MedicalConditions
    
    subcategory = fields.String(missing=None)

class MedicalConditionsOutputSchema(Schema):
    items = fields.Nested(MedicalConditionsSchema(many=True), missing = [])
    total_items = fields.Integer()

class MedicalFamilyHistSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MedicalFamilyHistory
        exclude = ('idx', 'created_at', 'updated_at')

    user_id = fields.Integer()
    medical_condition_id = fields.Integer()

    @post_load
    def make_object(self, data, **kwargs):
        return MedicalFamilyHistory(**data)

class MedicalFamilyHistInputSchema(Schema):
    conditions = fields.Nested(MedicalFamilyHistSchema, many=True)

class MedicalFamilyHistOutputSchema(Schema):
    items = fields.Nested(MedicalFamilyHistSchema(many=True), missing = [])
    total_items = fields.Integer()

class MedicalImagingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MedicalImaging
        load_instance = True
        exclude = ["user_id", "idx"]

    possible_image_types = ['CT', 'MRI', 'PET', 'Scopes', 'Special imaging', 'Ultrasound', 'X-ray']
    image_type = fields.String(validate=validate.OneOf(possible_image_types), required=True)
    image_date = fields.Date(required=True)
    image_read = fields.String(required=True)
    reporter_firstname = fields.String(description="first name of reporting physician", dump_only=True)
    reporter_lastname = fields.String(description="last name of reporting physician", dump_only=True)
    reporter_id = fields.Integer(description="id of reporting physician", missing=None)

class MedicalBloodTestSchema(Schema):
    test_id = fields.Integer()
    user_id = fields.Integer()
    date = fields.Date(required=True)
    panel_type = fields.String(required=False)
    notes = fields.String(required=False)
    reporter_firstname = fields.String(description="first name of reporting physician", dump_only=True)
    reporter_lastname = fields.String(description="last name of reporting physician", dump_only=True)
    reporter_id = fields.Integer(description="id of reporting physician")

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
    user_id = fields.Integer()
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
    panel_type = fields.String()
    date = fields.Date(format="iso")
    reporter_firstname = fields.String(description="first name of reporting physician", dump_only=True)
    reporter_lastname = fields.String(description="last name of reporting physician", dump_only=True)
    reporter_id = fields.Integer(description="id of reporting physician", dump_only=True)

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
    test_id = fields.Integer()
    result_id = fields.Integer()
    result_value = fields.Float()

    @post_load
    def make_object(self, data, **kwargs):
        return MedicalBloodTestResults(**data)

class MedicalBloodTestResultTypesSchema(Schema):
    result_id = fields.Integer()
    result_name = fields.String()

class MedicalBloodTestTypes(ma.SQLAlchemyAutoSchema):
    class Meta():
        model = MedicalBloodTestResultTypes
        exclude = ('created_at', 'result_id')

class MedicalBloodTestResultTypesSchema(Schema):
    
    items = fields.Nested(MedicalBloodTestTypes(many=True)) 
    total = fields.Integer()
    
    @post_load
    def make_object(self, data, **kwargs):
        return MedicalBloodTestResultTypes(**data)

class MedicalHistorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MedicalHistory
        
    user_id = fields.Integer(missing=0)
    
    @post_load
    def make_object(self, data, **kwargs):
        return MedicalHistory(**data)
    
class MedicalPhysicalExamSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MedicalPhysicalExam
        exclude = ('idx', 'reporter_id')
        
    user_id = fields.Integer(missing=0)
    vital_height = fields.String(description="Deprecated, use vital_height_inches instead", missing="")
    reporter_firstname = fields.String(description="first name of reporting physician", dump_only=True)
    reporter_lastname = fields.String(description="last name of reporting physician", dump_only=True)
    reporter_id = fields.Integer(description="id of reporting physician", dump_only=True)

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

    user_id = fields.Integer(missing=0)
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