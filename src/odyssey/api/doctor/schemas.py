import logging
logger = logging.getLogger(__name__)

from marshmallow import Schema, fields, post_load, validate, pre_dump, validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from odyssey import ma
from odyssey.api.doctor.models import ( 
    MedicalBloodPressures,
    MedicalLookUpBloodPressureRange,
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
from odyssey.api.facility.models import MedicalInstitutions
from odyssey.utils.constants import  MEDICAL_CONDITIONS
from odyssey.utils.base.schemas import BaseSchema

"""
    Schemas for the doctor's API
"""

    
class MedicalBloodPressuresSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MedicalBloodPressures
        exclude = ('created_at',)
        dump_only = ('timestamp','idx', 'reporter_id', 'user_id')
        include_fk = True
        
    timestamp = fields.DateTime()
    systolic = fields.Float(metadata={'description':'units mmHg'},required=True)
    diastolic = fields.Float(metadata={'description':'units mmHg'},required=True)
    datetime_taken = fields.String(metadata={'description':'Date and time the blood pressure was taken'}, required=True)
    reporter_firstname = fields.String(metadata={'description': 'first name of reporting physician'}, dump_only=True)
    reporter_lastname = fields.String(metadata={'description': 'last name of reporting physician'}, dump_only=True)
    

    @post_load
    def make_object(self, data, **kwargs):
        return MedicalBloodPressures(**data)

class MedicalBloodPressuresOutputSchema(Schema):
    items = fields.Nested(MedicalBloodPressuresSchema(many=True), missing=[])
    total_items = fields.Integer()


class MedicalLookUpBloodPressureRangesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MedicalLookUpBloodPressureRange

class MedicalLookUpBloodPressureRangesOutputSchema(Schema):
    items = fields.Nested(MedicalLookUpBloodPressureRangesSchema(many=True),missing=[])
    total_items = fields.Integer()

class CheckBoxDeleteSchema(Schema):
    idx = fields.Integer()

class CheckBoxArrayDeleteSchema(Schema):
    delete_ids = fields.Nested(CheckBoxDeleteSchema(many=True))

class MedicalLookUpSTDSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MedicalLookUpSTD

class MedicalSTDHistorySchema(BaseSchema):
    class Meta:
        model = MedicalSTDHistory
        exclude = ('user_id',)
        include_fk = True
        load_instance = True

class MedicalSTDHistoryInputSchema(Schema):
    stds = fields.Nested(MedicalSTDHistorySchema(many=True))

class MedicalLookUpSTDOutputSchema(Schema):
    items = fields.Nested(MedicalLookUpSTDSchema(many=True),missing=[])
    total_items = fields.Integer()
 
class MedicalSocialHistorySchema(Schema):
    ever_smoked = fields.Boolean(missing=None, allow_none=True)
    currently_smoke = fields.Boolean(missing=None, allow_none=True)
    avg_num_cigs = fields.Integer(missing=None, allow_none=True)
    avg_weekly_drinks = fields.Integer(missing=None, allow_none=True)
    avg_weekly_workouts = fields.Integer(missing=None, allow_none=True)
    job_title = fields.String(missing=None, allow_none=True, validate=validate.Length(max=99))
    avg_hourly_meditation = fields.Integer(missing=None, allow_none=True)
    sexual_preference = fields.String(missing=None, allow_none=True)
    last_smoke_date = fields.Date(missing=None, allow_none=True, dump_only=True)
    last_smoke = fields.Integer(missing=None, allow_none=True)
    num_years_smoked = fields.Integer(missing=None, allow_none=True)
    plan_to_stop = fields.Boolean(missing=None, allow_none=True)

    # Must include empty string, because checking whether this is needed
    # happens only after schema validation. In the mean time, a missing
    # value of None, will get converted to empty string.
    possible_date_units = ['', 'days', 'months', 'years']

    last_smoke_time = fields.String(
        missing='',
        allow_none=True,
        metadata={'description': 'days, months, years'},
        validate=validate.OneOf(possible_date_units))

    @post_load
    def make_object(self, data, **kwargs):
        return MedicalSocialHistory(**data)

class MedicalSocialHistoryOutputSchema(Schema):
    social_history = fields.Nested(MedicalSocialHistorySchema, missing=None)
    std_history = fields.Nested(MedicalSTDHistorySchema(many=True), missing=None)

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

class MedicalFamilyHistSchema(BaseSchema):
    class Meta:
        model = MedicalFamilyHistory

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
        dump_only = ("user_id", "idx", "image_size", "image_path", "updated_at", "created_at")
        required = ("image_date", "image_read", "image_type")

    possible_image_types = ['CT', 'MRI', 'PET', 'Scopes', 'Special imaging', 'Ultrasound', 'X-ray']
    image_type = fields.String(validate=validate.OneOf(possible_image_types))
    reporter_firstname = fields.String(metadata={'description': 'first name of reporting physician'}, dump_only=True)
    reporter_lastname = fields.String(metadata={'description': 'last name of reporting physician'}, dump_only=True)
    reporter_id = fields.Integer(metadata={'description': 'id of reporting physician'}, missing=None)


class ReporterInfoSchema(Schema):
    firstname = fields.String()
    lastname = fields.String()
    profile_pictures = fields.Dict(keys=fields.String, values=fields.Url())


class MedicalImagingOutputSchema(Schema):
    reporter_infos = fields.Dict(keys=fields.Integer, values=fields.Nested(ReporterInfoSchema()))
    images = fields.Nested(MedicalImagingSchema(many=True))
    total_images = fields.Integer()


class MedicalBloodTestSchema(Schema):
    test_id = fields.Integer()
    user_id = fields.Integer()
    date = fields.Date(required=True)
    notes = fields.String(required=False)
    reporter_firstname = fields.String(metadata={'description': 'first name of reporting physician'}, dump_only=True)
    reporter_lastname = fields.String(metadata={'description': 'last name of reporting physician'}, dump_only=True)
    reporter_id = fields.Integer(metadata={'description': 'id of reporting physician'})
    reporter_profile_pictures = fields.Dict(keys=fields.Str(), values=fields.Str(), dump_only=True)
    image = fields.String(dump_only=True)
    was_fasted = fields.Boolean()

    @post_load
    def make_object(self, data, **kwargs):
        return MedicalBloodTests(**data)

class AllMedicalBloodTestSchema(Schema):
    """
    For returning several blood test instance details 
    No actual results are returned, just details on
    the test entry (notes, date)
    """
    items = fields.Nested(MedicalBloodTestSchema(many=True))
    total = fields.Integer()
    clientid = fields.Integer()

class MedicalBloodTestResultsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MedicalBloodTestResults
        dump_only = ('age', 'race', 'menstrual_cycle', 'biological_sex_male', 'evaluation')
        exclude = ('created_at','updated_at', 'idx')
    modobio_test_code = fields.String()

class MedicalBloodTestsInputSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MedicalBloodTests
        dump_only = ('reporter_id', 'test_id', 'panel_type', 'image_path')
        exclude = ('created_at', 'updated_at')
    user_id = fields.Integer(dump_only=True)
    results = fields.Nested(MedicalBloodTestResultsSchema, many=True)
    was_fasted = fields.Boolean(required = False, missing = None)

class BloodTestsByTestID(Schema):
    """
    Organizes blood test results into a nested results field
    General information about the test entry like testid, date, notes, panel
    are in the outer most part of this schema.
    """
    test_id = fields.Integer()
    results = fields.Nested(MedicalBloodTestResultsSchema(many=True))
    notes = fields.String()
    date = fields.Date(format="iso")
    image = fields.String()
    reporter_firstname = fields.String(metadata={'description': 'first name of reporting physician'}, dump_only=True)
    reporter_lastname = fields.String(metadata={'description': 'last name of reporting physician'}, dump_only=True)
    reporter_id = fields.Integer(metadata={'description': 'id of reporting physician'}, dump_only=True)
    reporter_profile_pictures = fields.Dict(keys=fields.Str(), values=fields.Str(), dump_only=True)
    was_fasted = fields.Boolean()

class MedicalBloodTestResultsOutputSchema(Schema):
    """
    Schema for outputting a nested json 
    of blood test results. 
    """
    tests = fields.Integer(metadata={'description': '# of test entry sessions. All each test may have more than one test result'})
    test_results = fields.Integer(metadata={'description': '# of test results'})
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
    vital_height = fields.String(metadata={'description': 'Deprecated, use vital_height_inches instead'}, missing="")
    reporter_firstname = fields.String(metadata={'description': 'first name of reporting physician'}, dump_only=True)
    reporter_lastname = fields.String(metadata={'description': 'last name of reporting physician'}, dump_only=True)
    reporter_id = fields.Integer(metadata={'description': 'id of reporting physician'}, dump_only=True)

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
        dump_only = ('surgery_id', 'user_id', 'reporter_id')
        include_fk = True

    surgery_category = fields.String(validate=validate.OneOf(MEDICAL_CONDITIONS['Surgery'].keys()))

    @post_load
    def make_object(self, data, **kwargs):
        return MedicalSurgeries(**data)