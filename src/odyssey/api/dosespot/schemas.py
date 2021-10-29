from marshmallow import Schema, fields, post_load

from odyssey import ma
from odyssey.api.dosespot.models import ( 
    DoseSpotPractitionerID,
    DoseSpotPatientID,
    DoseSpotProxyID
)
from odyssey.utils.base.schemas import BaseSchema

"""
    Schemas for the DoseSpot's API
"""

class DoseSpotPrescribedStateSchedules(Schema):
    StateName = fields.String()
    Schedule = fields.Integer()

class DoseSpotPrescribedGET(Schema):
    PrescriptionId = fields.Integer(missing=None)
    WrittenDate = fields.Date(missing=None)
    Directions = fields.String(missing=None)
    Quantity = fields.String(missing=None)
    DispenseUnitId = fields.Integer(missing=None)
    DispenseUnitDescription = fields.String(missing=None)
    Refills = fields.String(missing=None)
    DaysSupply = fields.String(missing=None)
    PharmacyId = fields.Integer(missing=None)
    PharmacyNotes = fields.String(missing=None)
    NoSubstitutions = fields.Boolean(missing=None)
    EffectiveDate = fields.Date(missing=None)
    LastFillDate = fields.Date(missing=None)
    PrescriberId = fields.Integer(missing=None)
    PrescriberAgendId = fields.Integer(missing=None)
    RxReferenceNumber = fields.String(missing=None)
    Status = fields.Integer(missing=None)
    Formulary = fields.Boolean(missing=None)
    EligibilityId = fields.Integer(missing=None)
    Type = fields.Integer(missing=None)
    NonDoseSpotPrescriptionId = fields.String(missing=None)
    ErrorIgnored = fields.Boolean(missing=None)
    SupplyId = fields.Integer(missing=None)
    CompoundId = fields.Integer(missing=None)
    FreeTextType = fields.Integer(missing=None)
    ClinicId = fields.Integer(missing=None)
    SupervisorId = fields.Integer(missing=None)
    IsUrgent = fields.Boolean(missing=None)
    PatientMedicationId = fields.Integer(missing=None)
    MedicationStatus = fields.Integer(missing=None)
    Comment = fields.String(missing=None)
    DateInactive = fields.Date(missing=None)
    Encounter = fields.String(missing=None)
    DoseForm = fields.String(missing=None)
    Route = fields.String(missing=None)
    Strength = fields.String(missing=None)
    GenericProductName = fields.String(missing=None)
    LexiGenProductId = fields.Integer(missing=None)
    LexiDrugSynId = fields.Integer(missing=None)
    LexiSynonymTypeId = fields.Integer(missing=None)
    LexiGenDrugId = fields.String(missing=None)
    RxCUI = fields.String(missing=None)
    OTC = fields.Boolean(missing=None)
    NDC = fields.String(missing=None)
    Schedule = fields.String(missing=None)
    DisplayName = fields.String(missing=None)
    MonographPath = fields.String(missing=None)
    DrugClassification = fields.String(missing=None)
    StateSchedules = fields.Nested(DoseSpotPrescribedStateSchedules(many=True),missing=[])
    Brand = fields.Boolean(missing=None)
    modobio_id = fields.String(missing=None)
    modobio_user_id = fields.Integer(missing=None)
    modobio_name_id = fields.String(missing=None)


class DoseSpotPrescribedOutput(Schema):
    items = fields.Nested(DoseSpotPrescribedGET(many=True),missing=[])
    total_items = fields.Integer()

class DoseSpotAllergyGET(Schema):
    PatientAllergyId = fields.Integer(missing=None)
    Name = fields.String(missing=None)
    Code = fields.String(missing=None)
    RxCUI = fields.String(missing=None)
    CodeType = fields.Integer(missing=None)
    Reaction = fields.String(missing=None)
    ReactionType = fields.Integer(missing=None)
    StatusType = fields.Integer(missing=None)
    OnsetDate = fields.Date(missing=None)
    LastUpdatedUserId = fields.Integer(missing=None)
    modobio_id = fields.String(missing=None)
    modobio_user_id = fields.Integer(missing=None)
    modobio_name_id = fields.String(missing=None)

class DoseSpotAllergyOutput(Schema):
    items = fields.Nested(DoseSpotAllergyGET(many=True),missing=[])
    total_items = fields.Integer()

class DoseSpotEnrollmentGET(Schema):
    status = fields.String()

class DoseSpotEnrollmentSchema(Schema):
    status = fields.String()

class DoseSpotPrescribeSSO(Schema):
    url = fields.String()

class DoseSpotPharmacySelect(Schema):
    pharmacy_id = fields.Integer()
    primary_pharm = fields.Boolean(default=False)

class DoseSpotPharmacyNestedSelect(Schema):
    items = fields.Nested(DoseSpotPharmacySelect(many=True))

class DoseSpotCreateProxyUserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DoseSpotProxyID
        exclude = ('created_at',)
        dump_only = ('idx',)
    @post_load
    def make_object(self,data,**kwargs):
        return DoseSpotProxyID(**data)
class DoseSpotCreatePractitionerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DoseSpotPractitionerID
        exclude = ('created_at',)
        dump_only = ('idx','user_id')
        include_fk = True

    @post_load
    def make_object(self, data, **kwargs):
        return DoseSpotPractitionerID(**data)

class DoseSpotCreatePatientSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DoseSpotPatientID
        exclude = ('created_at',)
        dump_only = ('idx','user_id')
        include_fk = True

    @post_load
    def make_object(self, data, **kwargs):
        return DoseSpotPatientID(**data)


