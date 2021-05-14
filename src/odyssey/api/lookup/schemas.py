from marshmallow import Schema, fields, post_load

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
    LookupProfessionColors,
    LookupRoles
)

class LookupTermsAndConditionsOutputSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupTermsAndConditions
        exclude = ('idx','created_at')
    terms_and_conditions = fields.String(dump_only=True)

class LookupBookingTimeIncrementsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupBookingTimeIncrements

class LookupBookingTimeIncrementsOutputSchema(Schema):
    items = fields.Nested(LookupBookingTimeIncrementsSchema(many=True),missing=[])
    total_items = fields.Integer()

class LookupTimezones(Schema):
    items = fields.List(fields.String,missing = [])
    total_items = fields.Integer()

class LookupProfessionalAppointmentConfirmationWindowSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupProfessionalAppointmentConfirmationWindow

class LookupProfessionalAppointmentConfirmationWindowOutputSchema(Schema):
    items = fields.Nested(LookupProfessionalAppointmentConfirmationWindowSchema(many=True),missing=[])
    total_items = fields.Integer()

class LookupTransactionTypesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupTransactionTypes

class LookupTransactionTypesOutputSchema(Schema):
    items = fields.Nested(LookupTransactionTypesSchema(many=True),missing=[])
    total_items = fields.Integer()

class LookupCountriesOfOperationsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupCountriesOfOperations

class LookupCountriesOfOperationsOutputSchema(Schema):
    items = fields.Nested(LookupCountriesOfOperationsSchema(many=True),missing=[])
    total_items = fields.Integer()

class LookupClientBookingWindowSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupClientBookingWindow

class LookupClientBookingWindowOutputSchema(Schema):
    items = fields.Nested(LookupClientBookingWindowSchema(many=True),missing=[])
    total_items = fields.Integer()

class LookupTelehealthSessionDurationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupTelehealthSessionDuration

class LookupTelehealthSessionDurationOutputSchema(Schema):
    items = fields.Nested(LookupTelehealthSessionDurationSchema(many=True),missing=[])
    total_items = fields.Integer()

class LookupActivityTrackersSchema(ma.SQLAlchemyAutoSchema):
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

class LookupDrinkIngredientsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupDrinkIngredients
        exclude = ('idx', 'created_at', 'updated_at')

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

class LookupGoalsOutputSchema(Schema):
    items = fields.Nested(LookupGoalsSchema(many=True), missing = [])
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

class LookupDefaultHealthMetricsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupDefaultHealthMetrics
        exclude = ('created_at', 'updated_at', 'idx')

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

class LookupEmergencyNumbersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupEmergencyNumbers
        exclude = ('created_at', 'updated_at', 'idx')

class LookupEmergencyNumbersOutputSchema(Schema):
    items = fields.Nested(LookupEmergencyNumbersSchema(many=True), missing=[])
    total_items = fields.Integer()

class LookupProfessionColorsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupProfessionColors
        exclude = ('created_at', 'updated_at', 'idx')

class LookupProfessionColorsOutputSchema(Schema):
    items = fields.Nested(LookupProfessionColorsSchema(many=True), missing=[])
    total_items = fields.Integer()

class LookupRolesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupRoles
        exclude = ('created_at', 'updated_at')

class LookupRolesOutputSchema(Schema):
    items = fields.Nested(LookupRolesSchema(many=True), missing=[])
    total_items = fields.Integer()