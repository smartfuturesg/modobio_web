from marshmallow import Schema, fields, post_load, validate

from odyssey import ma
from odyssey.api.lookup.models import (
    LookupActivityTrackers, 
    LookupBookingTimeIncrements,
    LookupClinicalCareTeamResources,
    LookupClientBookingWindow,
    LookupCountriesOfOperations,
    LookupDefaultHealthMetrics,
    LookupDrinks, 
    LookupDrinkIngredients,
    LookupEHRPages, 
    LookupGoals, 
    LookupProfessionalAppointmentConfirmationWindow,
    LookupRaces,
    LookupSubscriptions,
    LookupTelehealthSessionDuration,
    LookupTermsAndConditions,
    LookupTerritoriesofOperation,
    LookupTransactionTypes,
    LookupNotifications,
    LookupEmergencyNumbers,
    LookupRoles,
    LookupMacroGoals,
    LookupLegalDocs,
    LookupMedicalSymptoms,
    LookupOrganizations,
    LookupCurrencies
)
from odyssey.utils.base.schemas import BaseSchema

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

class LookupTransactionTypesSchema(BaseSchema):
    class Meta:
        model = LookupTransactionTypes

class LookupTransactionTypesOutputSchema(Schema):
    items = fields.Nested(LookupTransactionTypesSchema(many=True),missing=[])
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

class LookupCareTeamResourcesDisplayNamesSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema only used for requrning display names, excluding resource_id
    This will eventually replace the schema above

    """
    class Meta:
        model = LookupClinicalCareTeamResources
        exclude = ('created_at', 'updated_at', 'resource_name', 'resource_id')


class LookupCareTeamResourcesOutputSchema(Schema):
    items = fields.Nested(LookupCareTeamResourcesSchema(many=True), missing = [])
    total_items = fields.Integer()

class LookupEHRPagesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupEHRPages
        exclude = ('created_at', 'updated_at', 'resource_group_name')
    
    resources = fields.Nested(LookupCareTeamResourcesDisplayNamesSchema(many=True), missing = [])
    
    @post_load
    def make_object(self, data, **kwargs):
        return LookupEHRPages(**data)


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


class LookupTerritoriesofOperationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupTerritoriesofOperation
        exclude = ('created_at', 'updated_at')

    @post_load
    def make_object(self, data, **kwargs):
        return LookupTerritoriesofOperation(**data)

class LookupTerritoriesofOperationOutputSchema(Schema):
    items = fields.Nested(LookupTerritoriesofOperationSchema(many=True), missing = [])
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
        exclude = ('created_at', 'updated_at')

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