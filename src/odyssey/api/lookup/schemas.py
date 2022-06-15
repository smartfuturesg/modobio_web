import logging
logger = logging.getLogger(__name__)

from marshmallow import Schema, fields, post_load, validate

from odyssey import ma
from odyssey.api.lookup.models import *
from odyssey.utils.base.schemas import BaseSchema

class LookupNotificationSeveritySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupNotificationSeverity

class LookupNotificationSeverityOutputSchema(Schema):
    items = fields.Nested(LookupNotificationSeveritySchema(many=True))
    total_items = fields.Integer()

class LookupUSStatesSchema(ma.SQLAlchemyAutoSchema):
    
    territory_id = fields.Integer(missing=None)
    idx = fields.Integer(missing=None)
    state = fields.String()
    abbreviation = fields.String()
    active = fields.Bool()
class LookupUSStatesOutputSchema(Schema):
    items = fields.Nested(LookupUSStatesSchema(many=True))
    total_items = fields.Integer()

class LookupTermsAndConditionsOutputSchema(BaseSchema):
    class Meta:
        model = LookupTermsAndConditions

    terms_and_conditions = fields.String(dump_only=True)

class LookupBookingTimeIncrementsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        exclude = ('created_at', 'updated_at')
        model = LookupBookingTimeIncrements

class LookupBookingTimeIncrementsOutputSchema(Schema):
    items = fields.Nested(LookupBookingTimeIncrementsSchema(many=True),missing=[])
    total_items = fields.Integer()

class LookupTimezones(Schema):
    items = fields.List(fields.String,missing = [])
    total_items = fields.Integer()

class LookupProfessionalAppointmentConfirmationWindowSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        exclude = ('created_at', 'updated_at')
        model = LookupProfessionalAppointmentConfirmationWindow

class LookupProfessionalAppointmentConfirmationWindowOutputSchema(Schema):
    items = fields.Nested(LookupProfessionalAppointmentConfirmationWindowSchema(many=True),missing=[])
    total_items = fields.Integer()


class LookupCountriesOfOperationsSchema(BaseSchema):
    class Meta:
        model = LookupCountriesOfOperations

class LookupCountriesOfOperationsOutputSchema(Schema):
    items = fields.Nested(LookupCountriesOfOperationsSchema(many=True),missing=[])
    total_items = fields.Integer()

class LookupClientBookingWindowSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        exclude = ('created_at', 'updated_at')
        model = LookupClientBookingWindow

class LookupClientBookingWindowOutputSchema(Schema):
    items = fields.Nested(LookupClientBookingWindowSchema(many=True),missing=[])
    total_items = fields.Integer()

class LookupTelehealthSessionDurationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        exclude = ('created_at', 'updated_at')
        model = LookupTelehealthSessionDuration

class LookupTelehealthSessionDurationOutputSchema(Schema):
    items = fields.Nested(LookupTelehealthSessionDurationSchema(many=True),missing=[])
    total_items = fields.Integer()

class LookupActivityTrackersSchema(BaseSchema):
    class Meta:
        model = LookupActivityTrackers

class LookupActivityTrackersOutputSchema(Schema):
    items = fields.Nested(LookupActivityTrackersSchema(many=True),missing=[])
    total_items = fields.Integer()

class LookupDrinksSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupDrinks
        exclude = ('created_at', 'updated_at')

    primary_ingredient = fields.String()
    goal = fields.String()

    @post_load
    def make_object(self, data, **kwargs):
        return LookupDrinks(**data)

class LookupDrinksOutputSchema(Schema):
    items = fields.Nested(LookupDrinksSchema(many=True), missing = [])
    total_items = fields.Integer()

class LookupDrinkIngredientsSchema(BaseSchema):
    class Meta:
        model = LookupDrinkIngredients

    @post_load
    def make_object(self, data, **kwargs):
        return LookupDrinkIngredients(**data)

class LookupDrinkIngredientsOutputSchema(Schema):
    items = fields.Nested(LookupDrinkIngredientsSchema(many=True), missing = [])
    total_items = fields.Integer()

class LookupGoalsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupGoals
        exclude = ('created_at', 'updated_at')

    @post_load
    def make_object(self, data, **kwargs):
        return LookupGoals(**data)

class LookupCareTeamResourcesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupClinicalCareTeamResources
        exclude = ('created_at', 'updated_at', 'resource_name')

    @post_load
    def make_object(self, data, **kwargs):
        return LookupClinicalCareTeamResources(**data)

class LookupCareTeamResourcesOutputSchema(Schema):
    items = fields.Nested(LookupCareTeamResourcesSchema(many=True), missing = [])
    total_items = fields.Integer()

class LookupEHRPagesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupClinicalCareTeamResources
        exclude = ('created_at', 'updated_at', 'resource_group','access_group', 'resource_name')
    
    display_grouping = fields.String()

    @post_load
    def make_object(self, data, **kwargs):
        return LookupClinicalCareTeamResources(**data)


class LookupEHRPagesOutputSchema(Schema):
    items = fields.Nested(LookupEHRPagesSchema(many=True), missing = [])
    total_items = fields.Integer()

class LookupGoalsOutputSchema(Schema):
    items = fields.Nested(LookupGoalsSchema(many=True), missing = [])
    total_items = fields.Integer()

class LookupMacroGoalsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupMacroGoals
        exclude = ('created_at', 'updated_at')

class LookupMacroGoalsOutputSchema(Schema):
    items = fields.Nested(LookupMacroGoalsSchema(many=True), missing = [])
    total_items = fields.Integer()

class LookupRacesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupRaces
        exclude = ('created_at', 'updated_at')

    @post_load
    def make_object(self, data, **kwargs):
        return LookupRaces(**data)

class LookupRacesOutputSchema(Schema):
    items = fields.Nested(LookupRacesSchema(many=True), missing = [])
    total_items = fields.Integer()

class LookupSubscriptionsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupSubscriptions
        exclude = ('created_at', 'updated_at')

    @post_load
    def make_object(self, data, **kwargs):
        return LookupSubscriptions(**data)

class LookupSubscriptionsOutputSchema(Schema):
    items = fields.Nested(LookupSubscriptionsSchema(many=True), missing = [])
    total_items = fields.Integer()

class LookupNotificationsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupNotifications
        exclude = ('created_at', 'updated_at')

    @post_load
    def make_object(self, data, **kwargs):
        return LookupNotifications(**data)

class LookupDefaultHealthMetricsSchema(BaseSchema):
    class Meta:
        model = LookupDefaultHealthMetrics

    @post_load
    def make_object(self, data, **kwargs):
        return LookupDefaultHealthMetrics(**data)

class LookupDefaultHealthMetricsOutputSchema(Schema):
    items = fields.Nested(LookupDefaultHealthMetricsSchema(many=True), missing = [])
    total_items = fields.Integer()


class LookupTerritoriesOfOperationsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupTerritoriesOfOperations
        exclude = ('created_at', 'updated_at')

    @post_load
    def make_object(self, data, **kwargs):
        return LookupTerritoriesOfOperations(**data)

class LookupTerritoriesOfOperationsOutputSchema(Schema):
    items = fields.Nested(LookupTerritoriesOfOperationsSchema(many=True), missing = [])
    total_items = fields.Integer()

class LookupNotificationsOutputSchema(Schema):
    items = fields.Nested(LookupNotificationsSchema(many=True), missing = [])
    total_items = fields.Integer()

class LookupTelehealthSettingsSchema(Schema):
    session_durations = fields.Nested(LookupTelehealthSessionDurationOutputSchema, missing = [])
    booking_windows = fields.Nested(LookupClientBookingWindowOutputSchema, missing = [])
    confirmation_windows = fields.Nested(LookupProfessionalAppointmentConfirmationWindowOutputSchema, missing= [])

class LookupEmergencyNumbersSchema(BaseSchema):
    class Meta:
        model = LookupEmergencyNumbers

class LookupEmergencyNumbersOutputSchema(Schema):
    items = fields.Nested(LookupEmergencyNumbersSchema(many=True), missing=[])
    total_items = fields.Integer()

class LookupRolesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupRoles
        exclude = ('created_at', 'updated_at', 'color')

class LookupRolesOutputSchema(Schema):
    items = fields.Nested(LookupRolesSchema(many=True), missing=[])
    total_items = fields.Integer()

class LookupLegalDocsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupLegalDocs
        exclude = ('created_at', 'updated_at', 'path')

    target = fields.String(validate=validate.OneOf(('User', 'Professional', 'Practitioner')))
    content = fields.String(dump_only=True)
    idx = fields.Integer(dump_only=True)

class LookupLegalDocsOutputSchema(Schema):
    items = fields.Nested(LookupLegalDocsSchema(many=True), missing=[])
    total_items = fields.Integer()

class LookupMedicalSymptomsSchema(BaseSchema):
    class Meta:
        model = LookupMedicalSymptoms

class LookupMedicalSymptomsOutputSchema(Schema):
    items = fields.Nested(LookupMedicalSymptomsSchema(many=True), missing=[])
    total_items = fields.Integer()

class LookupOrganizationsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupOrganizations
        exclude = ('created_at', 'updated_at', 'org_token')

class LookupOrganizationsOutputSchema(Schema):
    items = fields.Nested(LookupOrganizationsSchema(many=True), missing=[])
    total_items = fields.Integer()

class LookupCurrenciesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupCurrencies
        exclude = ('created_at', 'updated_at')

class LookupCurrenciesOutputSchema(Schema):
    items = fields.Nested(LookupCurrenciesSchema(many=True), missing=[])
    total_items = fields.Integer()
  
class LookupBloodTestsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupBloodTests
        exclude = ('created_at', 'updated_at')  
    
class LookupBloodTestsOutputSchema(Schema):
    items = fields.Nested(LookupBloodTestsSchema(many=True), missing=[])
    total_items = fields.Integer()
    
class LookupBloodTestRangesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupBloodTestRanges
        exclude = ('created_at', 'updated_at')
        
    race_id = fields.Integer()
    race = fields.String()
        
class LookupBloodTestRangesOutputSchema(Schema):
    items = fields.Nested(LookupBloodTestRangesSchema(many=True), missing=[])
    total_items = fields.Integer()
    
class LookupBloodTestRangesAllSchema(Schema):
    test = fields.Nested(LookupBloodTestsSchema)
    range = fields.Nested(LookupBloodTestRangesSchema)
    
class LookupBloodTestRangesAllOutputSchema(Schema):
    items = fields.Nested(LookupBloodTestRangesAllSchema(many=True), missing=[])
    total_items = fields.Integer()

class LookupDevNamesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupDevNames
        exclude = ('created_at', 'updated_at')

class LookupDevNamesOutputSchema(Schema):
    items = fields.Nested(LookupDevNamesSchema(many=True), missing=[])
    total_items = fields.Integer()
    
class LookupVisitReasonsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupVisitReasons
        exclude = ('created_at', 'updated_at')

class LookupVisitReasonsOutputSchema(Schema):
    items = fields.Nested(LookupVisitReasonsSchema(many=True), missing=[])
    total_items = fields.Integer()

class LookupEmotesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupEmotes
        exclude = ('created_at', 'updated_at')

class LookupEmotesOutputSchema(Schema):
    items = fields.Nested(LookupEmotesSchema(many=True), missing=[])
    total_items = fields.Integer()
    
    
class LookupMedicalConditionsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupMedicalConditions
    
    subcategory = fields.String(missing=None)

class LookupMedicalConditionsOutputSchema(Schema):
    items = fields.Nested(LookupMedicalConditionsSchema(many=True), missing = [])
    total_items = fields.Integer()
    
    
class LookupSTDsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupSTDs
        exclude = ('created_at', 'updated_at')
        
        
class LookupSTDsOutputSchema(Schema):
    items = fields.Nested(LookupSTDsSchema(many=True), missing = [])
    total_items = fields.Integer()
    
    
class LookupBloodPressureRangesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupBloodPressureRanges
        exclude = ('created_at', 'updated_at')
        
class LookupBloodPressureRangesOutputSchema(Schema):
    items = fields.Nested(LookupBloodPressureRangesSchema(many=True), missing = [])
    total_items = fields.Integer()