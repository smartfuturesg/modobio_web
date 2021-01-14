from marshmallow import Schema, fields, post_load, validate, pre_dump, validates, ValidationError

from odyssey import ma
from odyssey.api.doctor.models import ( 
    MedicalLookUpSTD,
    MedicalGeneralInfo,
    MedicalGeneralInfoMedications,
    MedicalGeneralInfoMedicationAllergy,
    MedicalFamilyHistory,
    MedicalConditions,
    MedicalHistory,
    MedicalPhysicalExam,
    MedicalImaging,
    MedicalBloodTests,
    MedicalBloodTestResults,
    MedicalBloodTestResultTypes,
    MedicalExternalMR,
    MedicalSocialHistory,
    MedicalSTDHistory,
    MedicalSurgeries
)
from odyssey.api.user.models import User
from odyssey.api.facility.models import MedicalInstitutions
from odyssey.utils.constants import MEDICAL_CONDITIONS

"""
    Schemas for the doctor's API
"""

class CheckBoxDeleteSchema(Schema):
    idx = fields.Integer()

class CheckBoxArrayDeleteSchema(Schema):
    delete_ids = fields.Nested(CheckBoxDeleteSchema(many=True))

class MedicalLookUpSTDSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MedicalLookUpSTD

class MedicalSTDHistorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MedicalSTDHistory
        exclude = ('idx', 'created_at', 'updated_at')

    user_id = fields.Integer()
    std_id = fields.Integer()
    
    @post_load
    def make_object(self, data, **kwargs):
        return MedicalSTDHistory(**data)

class MedicalSTDHistoryInputSchema(Schema):
    stds = fields.Nested(MedicalSTDHistorySchema(many=True))

class MedicalLookUpSTDOutputSchema(Schema):
    items = fields.Nested(MedicalLookUpSTDSchema(many=True),missing=[])
    total_items = fields.Integer()

class MedicalSocialHistorySchema(Schema):

    # user_id = fields.Integer()
    ever_smoked = fields.Boolean(missing=False)
    currently_smoke = fields.Boolean()
    avg_num_cigs = fields.Integer()
    avg_weekly_drinks = fields.Integer(missing=0)
    avg_weekly_workouts = fields.Integer(missing=0)
    job_title = fields.String(missing=None, validate=validate.Length(max=99))
    avg_hourly_meditation = fields.Integer(missing=0)
    sexual_preference = fields.String(missing=None)
    
    last_smoke_date = fields.Date(dump_only=True)
    last_smoke = fields.Integer(required=False,missing=None)

    possible_date_units = ['','days','months','years']

    last_smoke_time = fields.String(required=False,description="days, months, years",validate=validate.OneOf(possible_date_units),missing=None)
    num_years_smoked = fields.Integer(missing=0)
    plan_to_stop = fields.Boolean(missing=None)

    @post_load
    def make_object(self, data, **kwargs):
        return MedicalSocialHistory(**data)

class MedicalSocialHistoryOutputSchema(Schema):
    social_history = fields.Nested(MedicalSocialHistorySchema,missing=None)
    std_history = fields.Nested(MedicalSTDHistorySchema(many=True),missing=[])

class MedicalGeneralInfoMedicationAllergySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MedicalGeneralInfoMedicationAllergy
        exclude = ('created_at', 'updated_at')

    idx = fields.Integer()
    possible_allergy_symptoms = ['Rash', 'Vertigo', 'Nausea', 'Swelling', 'Diarrhea', 'Vomiting', 'Headache', 'Anaphylaxis', 'Blurred Vision', 'Abdominal Pain', 'Shortness of Breath']
    allergy_symptoms = fields.String(validate=validate.OneOf(possible_allergy_symptoms),missing=None)

    @post_load
    def make_object(self, data, **kwargs):
        return MedicalGeneralInfoMedicationAllergy(**data)

class MedicalGeneralInfoMedicationsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MedicalGeneralInfoMedications
        exclude = ('created_at', 'updated_at')
    
    idx = fields.Integer()
    @post_load
    def make_object(self, data, **kwargs):
        return MedicalGeneralInfoMedications(**data)

class MedicalGeneralInfoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MedicalGeneralInfo
        exclude = ('created_at', 'updated_at')
    
    idx = fields.Integer(dump_only=True)
    primary_doctor_contact_name = fields.String(missing=None)
    primary_doctor_contact_phone = fields.String(missing=None)
    primary_doctor_contact_email = fields.String(missing=None)
    blood_type = fields.String(missing=None)
    blood_type_positive = fields.Boolean(missing=None)
    
    @post_load
    def make_object(self, data, **kwargs):
        return MedicalGeneralInfo(**data)

class MedicalGeneralInfoInputSchema(Schema):
    gen_info = fields.Nested(MedicalGeneralInfoSchema, missing=None)
    medications = fields.Nested(MedicalGeneralInfoMedicationsSchema(many=True), missing = [])
    allergies = fields.Nested(MedicalGeneralInfoMedicationAllergySchema(many=True), missing = [])


class MedicalMedicationsInfoInputSchema(Schema):
    medications = fields.Nested(MedicalGeneralInfoMedicationsSchema(many=True), missing = [])

class MedicalAllergiesInfoInputSchema(Schema):
    allergies = fields.Nested(MedicalGeneralInfoMedicationAllergySchema(many=True), missing = [])

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

class MedicalExternalMRSchema(Schema):
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
        return MedicalExternalMR(**data)

class MedicalExternalMREntrySchema(Schema):
    """
    For returning medical institutions in GET request and also accepting new institute names
    """

    record_locators = fields.Nested(MedicalExternalMRSchema, many=True)
    
    @pre_dump
    def ravel(self, data, **kwargs):
        """upon dump, add back the schema structure"""
        response = {"record_locators": data}
        return response

class MedicalSurgeriesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MedicalSurgeries
        exclude = ('created_at', 'updated_at')
        dump_only = ('surgery_id', 'client_user_id', 'reporter_user_id')

    surgery_category = fields.String(validate=validate.OneOf(MEDICAL_CONDITIONS['Surgery'].keys()))

    @post_load
    def make_object(self, data, **kwargs):
        return MedicalSurgeries(**data)