from flask_accepts import responds
from flask_restx import Resource, Namespace

import pytz
import pathlib

from flask import current_app

from odyssey.utils.auth import token_auth
from odyssey.api.lookup.models import (
     LookupActivityTrackers,
     LookupBookingTimeIncrements,
     LookupClientBookingWindow,
     LookupClinicalCareTeamResources,
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
from odyssey.api.lookup.schemas import (
    LookupActivityTrackersOutputSchema,
    LookupBookingTimeIncrementsOutputSchema,
    LookupCareTeamResourcesOutputSchema,
    LookupCountriesOfOperationsOutputSchema,
    LookupDefaultHealthMetricsOutputSchema, 
    LookupDrinksOutputSchema, 
    LookupDrinkIngredientsOutputSchema,
    LookupEHRPagesOutputSchema, 
    LookupGoalsOutputSchema,
    LookupRacesOutputSchema,
    LookupSubscriptionsOutputSchema,
    LookupTerritoriesofOperationOutputSchema,
    LookupTermsAndConditionsOutputSchema,
    LookupTransactionTypesOutputSchema,
    LookupNotificationsOutputSchema,
    LookupCareTeamResourcesOutputSchema,
    LookupTimezones,
    LookupTelehealthSettingsSchema,
    LookupEmergencyNumbersOutputSchema,
    LookupRolesOutputSchema,
    LookupMacroGoalsOutputSchema,
    LookupLegalDocsOutputSchema,
    LookupNotificationsOutputSchema,
    LookupMedicalSymptomsOutputSchema,
    LookupOrganizationsOutputSchema,
    LookupCurrenciesOutputSchema
)
from odyssey.utils.misc import check_drink_existence

from odyssey import db

ns = Namespace('lookup', description='Endpoints for lookup tables.')

@ns.route('/terms-and-conditions/')
class LookupTermsAndConditionResource(Resource):
    """ Returns the Terms and Conditions
    """
    @responds(schema=LookupTermsAndConditionsOutputSchema,status_code=200,api=ns)
    def get(self):
        lookup_ts = LookupTermsAndConditions.query.one_or_none()
        payload = {}
        if lookup_ts:
            payload['terms_and_conditions'] = lookup_ts.terms_and_conditions
        else:
            payload['terms_and_conditions'] = 'Terms and Conditions'
        return payload

@ns.route('/telehealth/booking-increments/')
class LookupTelehealthBookingIncrements(Resource):
    """ Returns stored booking increments.
    Returns
    -------
    dict
        JSON encoded dict.
    """
    @responds(schema=LookupBookingTimeIncrementsOutputSchema,status_code=200, api=ns)
    def get(self):
                
        booking_increments = LookupBookingTimeIncrements.query.all()
        
        payload = {'items': booking_increments,
                   'total_items': len(booking_increments)}

        return payload

@ns.route('/timezones/')
class LookupTimezones(Resource):
    @token_auth.login_required
    @responds(schema=LookupTimezones,status_code=200,api=ns)
    def get(self):
        varArr = pytz.country_timezones['us']
        payload = {'items': varArr,
                   'total_items': len(varArr) }
        return payload

@ns.route('/business/transaction-types/')
class LookupTransactionTypesResource(Resource):
    """ Returns stored transaction types in database by GET request.
    Returns
    -------
    dict
        JSON encoded dict.
    """
    @responds(schema=LookupTransactionTypesOutputSchema,status_code=200, api=ns)
    def get(self):
                
        transaction_types = LookupTransactionTypes.query.all()
        
        payload = {'items': transaction_types,
                   'total_items': len(transaction_types)}

        return payload


@ns.route('/business/countries-of-operations/')
class LookupCountryOfOperationResource(Resource):
    """ Returns stored countries of operations in database by GET request.

    Returns
    -------
    dict
        JSON encoded dict.
    """
    @token_auth.login_required
    @responds(schema=LookupCountriesOfOperationsOutputSchema,status_code=200, api=ns)
    def get(self):
                
        countries = LookupCountriesOfOperations.query.all()
        
        payload = {'items': countries,
                   'total_items': len(countries)}

        return payload

@ns.route('/business/telehealth-settings/')
class LookupTelehealthSettingsApi(Resource):
    """ Endpoints related to the telehealth lookup tables """

    @token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
    @responds(schema=LookupTelehealthSettingsSchema, status_code=200, api=ns)
    def get(self):
        
        durations = {'items': LookupTelehealthSessionDuration.query.all()}
        durations['total_items'] = len(durations['items'])

        booking_windows = {'items': LookupClientBookingWindow.query.all()}
        booking_windows['total_items'] = len(booking_windows['items'])

        confirmation_windows = {'items': LookupProfessionalAppointmentConfirmationWindow.query.all()}
        confirmation_windows['total_items'] = len(confirmation_windows['items'])

        return {
            'session_durations': durations,
            'booking_windows' : booking_windows,
            'confirmation_windows': confirmation_windows,
        }

@ns.route('/activity-trackers/misc/')
class WearablesLookUpFitbitActivityTrackersResource(Resource):
    """ Returns misc activity trackers stored in the database in response to a GET request.

    Returns
    -------
    dict
        JSON encoded dict.
    """
    @token_auth.login_required
    @responds(schema=LookupActivityTrackersOutputSchema,status_code=200, api=ns)
    def get(self):
        
        delete_brands = ['Apple', 'Fitbit', 'Garmin', 'Samsung']
        
        activity_trackers = LookupActivityTrackers.query.filter(LookupActivityTrackers.brand.notin_(delete_brands)).all()
        
        payload = {'items': activity_trackers,
                   'total_items': len(activity_trackers)}

        return payload

@ns.route('/activity-trackers/fitbit/')
class WearablesLookUpFitbitActivityTrackersResource(Resource):
    """ Returns Fitbit activity trackers stored in the database in response to a GET request.

    Returns
    -------
    dict
        JSON encoded dict.
    """
    @token_auth.login_required
    @responds(schema=LookupActivityTrackersOutputSchema,status_code=200, api=ns)
    def get(self):
        activity_trackers = LookupActivityTrackers.query.filter_by(brand='Fitbit').all()
        payload = {'items': activity_trackers,
                   'total_items': len(activity_trackers)}

        return payload

@ns.route('/activity-trackers/apple/')
class WearablesLookUpAppleActivityTrackersResource(Resource):
    """ Returns activity Apple trackers stored in the database in response to a GET request.

    Returns
    -------
    dict
        JSON encoded dict.
    """
    @token_auth.login_required
    @responds(schema=LookupActivityTrackersOutputSchema,status_code=200, api=ns)
    def get(self):
        activity_trackers = LookupActivityTrackers.query.filter_by(brand='Apple').all()
        payload = {'items': activity_trackers,
                   'total_items': len(activity_trackers)}

        return payload

@ns.route('/activity-trackers/all/')
class WearablesLookUpAllActivityTrackersResource(Resource):
    """ Returns activity trackers stored in the database in response to a GET request.

    Returns
    -------
    dict
        JSON encoded dict.
    """
    @token_auth.login_required
    @responds(schema=LookupActivityTrackersOutputSchema,status_code=200, api=ns)
    def get(self):
        activity_trackers = LookupActivityTrackers.query.all()
        payload = {'items': activity_trackers,
                   'total_items': len(activity_trackers)}

        return payload

@ns.route('/drinks/')
class LookupDrinksApi(Resource):
    
    @token_auth.login_required
    @responds(schema=LookupDrinksOutputSchema, api=ns)
    def get(self):
        """get contents of drinks lookup table"""
        res = []
        for drink in LookupDrinks.query.all():
            drink.primary_ingredient = LookupDrinkIngredients.query.filter_by(drink_id=drink.drink_id).filter_by(is_primary_ingredient=True).first().ingredient_name
            drink.goal = LookupGoals.query.filter_by(goal_id=drink.primary_goal_id).first().goal_name
            res.append(drink)
        return {'total_items': len(res), 'items': res}

@ns.route('/drinks/ingredients/<int:drink_id>/')
@ns.doc('Id of the desired drink')
class LookupDrinkIngredientsApi(Resource):

    @token_auth.login_required
    @responds(schema=LookupDrinkIngredientsOutputSchema, api=ns)
    def get(self, drink_id):
        """get recipe of the drink denoted by drink_id"""
        check_drink_existence(drink_id)

        res = LookupDrinkIngredients.query.filter_by(drink_id=drink_id).all()
        return {'total_items': len(res), 'items': res}

@ns.route('/goals/')
class LookupGoalsApi(Resource):

    @token_auth.login_required
    @responds(schema=LookupGoalsOutputSchema, api=ns)
    def get(self):
        """get contents of goals lookup table"""
        res = LookupGoals.query.all()
        return {'total_items': len(res), 'items': res}

@ns.route('/macro-goals/')
class LookupMacroGoalsApi(Resource):

    @token_auth.login_required
    @responds(schema=LookupMacroGoalsOutputSchema, api=ns)
    def get(self):
        """get contents from macro goals lookup table"""
        res = LookupMacroGoals.query.all()
        return {'total_items': len(res), 'items': res}

@ns.route('/races/')
class LookupRacesApi(Resource):

    @token_auth.login_required
    @responds(schema=LookupRacesOutputSchema, api=ns)
    def get(self):
        """get contents of races lookup table"""
        res = LookupRaces.query.all()
        return {'total_items': len(res), 'items': res}

@ns.route('/care-team/resources/')
class LookupClinicalCareTeamResourcesApi(Resource):
    """
    To be replaced by care-team/ehr-resources/
    Returns available resources that can be shared within clinical care teams
    """
    # @token_auth.login_required
    @responds(schema=LookupCareTeamResourcesOutputSchema, api=ns)
    def get(self):
        """get contents of clinical care team resources lookup table"""
        res = LookupClinicalCareTeamResources.query.all()
        return {'total_items': len(res), 'items': res}

@ns.route('/care-team/ehr-resources/')
class LookupClinicalCareTeamResourcesApi(Resource):
    """
    Returns available resources that can be shared within clinical care teams
    """
    # @token_auth.login_required
    @responds(schema=LookupEHRPagesOutputSchema, api=ns)
    def get(self):
        # breakpoint()
        """get contents of clinical care team resources lookup table"""
        res = LookupEHRPages.query.all()
        return {'total_items': len(res), 'items': res}
        
@ns.route('/subscriptions/')
class LookupSubscriptionsApi(Resource):

    @token_auth.login_required
    @responds(schema=LookupSubscriptionsOutputSchema, api=ns)
    def get(self):
        """get contents of subscription plans lookup table"""
        res = LookupSubscriptions.query.all()
        return {'total_items': len(res), 'items': res}

@ns.route('/notifications/')
class LookupNotificationsApi(Resource):

    @token_auth.login_required
    @responds(schema=LookupNotificationsOutputSchema, api=ns)
    def get(self):
        """get contents of notification types lookup table"""
        res = LookupNotifications.query.all()
        return {'total_items': len(res), 'items': res}

@ns.route('/default-health-metrics/')
class LookupDefaultHealthMetricsApi(Resource):
    """
    Endpoint for handling requests for all default health metrics
    """

    @token_auth.login_required
    @responds(schema=LookupDefaultHealthMetricsOutputSchema, status_code=200, api=ns)
    def get(self):
        """get contents of default health metrics types lookup table"""
        res = LookupDefaultHealthMetrics.query.all()
        return {'total_items': len(res), 'items': res}

@ns.route('/operational-territories/')
class LookupTerritoriesofOperationApi(Resource):
    """
    Endpoint for handling requests for all territories of operation
    """
    @token_auth.login_required
    @responds(schema=LookupTerritoriesofOperationOutputSchema, status_code=200, api=ns)
    def get(self):
        """get contents of operational territories lookup table"""
        res = LookupTerritoriesofOperation.query.all()
        return {'total_items': len(res), 'items': res}

@ns.route('/emergency-numbers/')
class LookupEmergencyNumbersApi(Resource):
    """
    Endpoint that returns emergency phone number for the Ambulance service
    """
    @token_auth.login_required
    @responds(schema=LookupEmergencyNumbersOutputSchema, status_code=200, api=ns)
    def get(self):
        """GET request for the list of emergency numbers"""
        res = LookupEmergencyNumbers.query.filter_by(service='Ambulance').all()
        return {'total_items': len(res), 'items': res}

@ns.route('/roles/')
class LookupRolesApi(Resource):
    """
    Endpoint that returns the roles that exist for users.
    """
    @token_auth.login_required
    @responds(schema=LookupRolesOutputSchema, status_code=200, api=ns)
    def get(self):
        """get contents of roles lookup table"""
        res = LookupRoles.query.all()
        return {'total_items': len(res), 'items': res}

@ns.route('/legal-docs/')
class LookupLegalDocsApi(Resource):
    """
    Endpoint that returns the list of legal documents.
    """
    @token_auth.login_required
    @responds(schema=LookupLegalDocsOutputSchema, status_code=200, api=ns)
    def get(self):
        """get contents of legal docs lookup table"""
        res = LookupLegalDocs.query.all()
        for doc in res:
            html_file = pathlib.Path(current_app.static_folder) / doc.path
            with open(html_file) as fh:
                doc.content = fh.read()
        return {'total_items': len(res), 'items': res}

@ns.route('/medical-symptoms/')
class LookupMedicalSymptomssApi(Resource):
    """
    Endpoint that returns the list of medical symptoms.
    """
    @token_auth.login_required
    @responds(schema=LookupMedicalSymptomsOutputSchema, status_code=200, api=ns)
    def get(self):
        """get contents of medical symptoms lookup table"""
        res = LookupMedicalSymptoms.query.all()
        return {'total_items': len(res), 'items': res}

@ns.route('/organizations/')
class LookupOrganizationsApi(Resource):
    """
    Endpoint that returns the list of organizations affiliated with Modobio.
    """
    @token_auth.login_required
    @responds(schema=LookupOrganizationsOutputSchema, status_code=200, api=ns)
    def get(self):
        """get contents of medical symptoms lookup table"""
        res = LookupOrganizations.query.all()
        return {'total_items': len(res), 'items': res}

@ns.route('/currencies/')
class LookupCurrenciesApi(Resource):
    """
    Endpoint that returns the list of medical symptoms.
    """
    @token_auth.login_required
    @responds(schema=LookupCurrenciesOutputSchema, status_code=200, api=ns)
    def get(self):
        """get contents of medical symptoms lookup table"""
        res = LookupCurrencies.query.all()
        return {'total_items': len(res), 'items': res}