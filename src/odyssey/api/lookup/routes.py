import logging
import pathlib
import pytz
import random

from flask import current_app, request
from flask_accepts import responds
from flask_restx import Namespace

from werkzeug.exceptions import BadRequest

from odyssey.api.lookup.models import (
     LookupActivityTrackers,
     LookupBookingTimeIncrements,
     LookupClientBookingWindow,
     LookupClinicalCareTeamResources,
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
     LookupTerritoriesOfOperations,
     LookupTransactionTypes,
     LookupNotifications,
     LookupEmergencyNumbers,
     LookupRoles,
     LookupMacroGoals,
     LookupLegalDocs,
     LookupMedicalSymptoms,
     LookupOrganizations,
     LookupCurrencies,
     LookupNotificationSeverity,
     LookupBloodTests,
     LookupBloodTestRanges,
     LookupDevNames,
     LookupVisitReasons
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
    LookupTerritoriesOfOperationsOutputSchema,
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
    LookupCurrenciesOutputSchema,
    LookupUSStatesOutputSchema,
    LookupNotificationSeverityOutputSchema,
    LookupBloodTestsOutputSchema,
    LookupBloodTestRangesOutputSchema,
    LookupBloodTestRangesAllOutputSchema,
    LookupDevNamesOutputSchema,
    LookupVisitReasonsOutputSchema
)
from odyssey import db
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource
from odyssey.utils.misc import check_drink_existence

logger = logging.getLogger(__name__)

ns = Namespace('lookup', description='Endpoints for lookup tables.')

@ns.route('/notifications/severity/')
class LookupNotificationSeverityResource(BaseResource):
    """
        Returns notification severity and their respective color
    """
    @responds(schema=LookupNotificationSeverityOutputSchema,status_code=200,api=ns)
    def get(self):
        severity = LookupNotificationSeverity.query.all()
        payload = {'items': severity,
                   'total_items': len(severity)}

        return payload

@ns.route('/states/')
class LookupUSStatesResource(BaseResource):
    """
    Returns United States' states and their abbreviations
    """
    @responds(schema=LookupUSStatesOutputSchema,status_code=200,api=ns)
    def get(self):
        states = LookupTerritoriesOfOperations.query.all()
        payload = {'items': [ 
                        {'abbreviation': state.sub_territory_abbreviation,
                        'state': state.sub_territory,
                        'territory_id': state.idx,
                        'idx': state.idx ,
                        'active': state.active} for state in states ],
                   'total_items': len(states)}

        return payload

@ns.route('/terms-and-conditions/')
class LookupTermsAndConditionResource(BaseResource):
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
class LookupTelehealthBookingIncrements(BaseResource):
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
class LookupTimezones(BaseResource):
    @token_auth.login_required
    @responds(schema=LookupTimezones,status_code=200,api=ns)
    def get(self):
        varArr = pytz.country_timezones['us']
        payload = {'items': varArr,
                   'total_items': len(varArr) }
        return payload

@ns.route('/business/transaction-types/')
class LookupTransactionTypesResource(BaseResource):
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
class LookupCountryOfOperationResource(BaseResource):
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
class LookupTelehealthSettingsApi(BaseResource):
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
class WearablesLookUpFitbitActivityTrackersResource(BaseResource):
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
class WearablesLookUpFitbitActivityTrackersResource(BaseResource):
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
class WearablesLookUpAppleActivityTrackersResource(BaseResource):
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
class WearablesLookUpAllActivityTrackersResource(BaseResource):
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
class LookupDrinksApi(BaseResource):
    
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
class LookupDrinkIngredientsApi(BaseResource):

    @token_auth.login_required
    @responds(schema=LookupDrinkIngredientsOutputSchema, api=ns)
    def get(self, drink_id):
        """get recipe of the drink denoted by drink_id"""
        check_drink_existence(drink_id)

        res = LookupDrinkIngredients.query.filter_by(drink_id=drink_id).all()
        return {'total_items': len(res), 'items': res}

@ns.route('/goals/')
class LookupGoalsApi(BaseResource):

    @token_auth.login_required
    @responds(schema=LookupGoalsOutputSchema, api=ns)
    def get(self):
        """get contents of goals lookup table"""
        res = LookupGoals.query.all()
        return {'total_items': len(res), 'items': res}

@ns.route('/macro-goals/')
class LookupMacroGoalsApi(BaseResource):

    @token_auth.login_required
    @responds(schema=LookupMacroGoalsOutputSchema, api=ns)
    def get(self):
        """get contents from macro goals lookup table"""
        res = LookupMacroGoals.query.all()
        return {'total_items': len(res), 'items': res}

@ns.route('/races/')
class LookupRacesApi(BaseResource):

    @token_auth.login_required
    @responds(schema=LookupRacesOutputSchema, api=ns)
    def get(self):
        """get contents of races lookup table"""
        res = LookupRaces.query.all()
        return {'total_items': len(res), 'items': res}


@ns.route('/care-team/resources/')
@ns.deprecated
class LookupClinicalCareTeamResourcesApi(BaseResource):
    """
    To be replaced by care-team/ehr-resources/
    Returns available resources that can be shared within clinical care teams
    """
    @token_auth.login_required
    @responds(schema=LookupCareTeamResourcesOutputSchema, api=ns)
    def get(self):
        """get contents of clinical care team resources lookup table"""
        res = LookupClinicalCareTeamResources.query.all()
        return {'total_items': len(res), 'items': res}

@ns.route('/care-team/ehr-resources/')
class LookupClinicalCareTeamResourcesApi(BaseResource):
    """
    Returns available resources that can be shared within clinical care teams
    """
    @token_auth.login_required
    @responds(schema=LookupEHRPagesOutputSchema, api=ns)
    def get(self):
        """get contents of clinical care team resources lookup table"""
        care_team_resources = LookupClinicalCareTeamResources.query.all()

        # add display grouping details
        for dat in care_team_resources:
            dat.display_grouping = dat.access_group + (f'.{dat.resource_group}' if dat.resource_group else '')

        return {'total_items': len(care_team_resources), 'items': care_team_resources}
        
@ns.route('/subscriptions/')
class LookupSubscriptionsApi(BaseResource):

    @token_auth.login_required
    @responds(schema=LookupSubscriptionsOutputSchema, api=ns)
    def get(self):
        """get contents of subscription plans lookup table"""
        res = LookupSubscriptions.query.all()
        return {'total_items': len(res), 'items': res}

@ns.route('/notifications/')
class LookupNotificationsApi(BaseResource):

    @token_auth.login_required
    @responds(schema=LookupNotificationsOutputSchema, api=ns)
    def get(self):
        """get contents of notification types lookup table"""
        res = LookupNotifications.query.all()
        return {'total_items': len(res), 'items': res}

@ns.route('/default-health-metrics/')
class LookupDefaultHealthMetricsApi(BaseResource):
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
class LookupTerritoriesOfOperationsApi(BaseResource):
    """
    Endpoint for handling requests for all territories of operation
    """
    @token_auth.login_required
    @responds(schema=LookupTerritoriesOfOperationsOutputSchema, status_code=200, api=ns)
    def get(self):
        """get contents of operational territories lookup table"""
        res = LookupTerritoriesOfOperations.query.all()
        return {'total_items': len(res), 'items': res}

@ns.route('/emergency-numbers/')
class LookupEmergencyNumbersApi(BaseResource):
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
class LookupRolesApi(BaseResource):
    """
    Endpoint that returns the roles that exist for users.
    """
    @token_auth.login_required
    @responds(schema=LookupRolesOutputSchema, status_code=200, api=ns)
    def get(self):
        """get contents of active roles in lookup table"""
        res = LookupRoles.query.filter_by(active=True).all()
        return {'total_items': len(res), 'items': res}

@ns.route('/legal-docs/')
class LookupLegalDocsApi(BaseResource):
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
class LookupMedicalSymptomssApi(BaseResource):
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
class LookupOrganizationsApi(BaseResource):
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
class LookupCurrenciesApi(BaseResource):
    """
    Endpoint that returns the list of medical symptoms.
    """
    @token_auth.login_required
    @responds(schema=LookupCurrenciesOutputSchema, status_code=200, api=ns)
    def get(self):
        """get contents of medical symptoms lookup table"""
        res = LookupCurrencies.query.all()
        return {'total_items': len(res), 'items': res}
    
@ns.route('/bloodtests/')
class LookupBloodTestsApi(BaseResource):
    """
    Endpoint that returns the list of blood test types.
    """
    @token_auth.login_required
    @responds(schema=LookupBloodTestsOutputSchema, status_code=200, api=ns)
    def get(self):
        """get contents of blood tests lookup table"""
        res = LookupBloodTests.query.all()
        return {'total_items': len(res), 'items': res}
    
@ns.route('/bloodtests/ranges/<string:modobio_test_code>/')
@ns.doc(params={'modobio_test_code': 'Modobio Test Code for desired test'})
class LookupBloodTestRangesApi(BaseResource):
    """
    Endpoint that return blood test range information for the requested test.
    """
    @token_auth.login_required
    @responds(schema=LookupBloodTestRangesOutputSchema, status_code=200, api=ns)
    def get(self, modobio_test_code):
        """get all ranges for the requested blood test"""
        res = LookupBloodTestRanges.query.filter_by(modobio_test_code=modobio_test_code).all()
        for range in res:
            if range.race_id:
                range.race = LookupRaces.query.filter_by(race_id=range.race_id).one_or_none().race_name
            else:
                range.race = None
        return {'total_items': len(res), 'items': res}
    
@ns.route('/bloodtests/ranges/all/')
class LookupBloodTestRangesAllApi(BaseResource):
    """
    Endpoint that return blood test range information for the all tests.
    """
    @token_auth.login_required
    @responds(schema=LookupBloodTestRangesAllOutputSchema, status_code=200, api=ns)
    def get(self):
        """get all ranges for the all blood tests"""
        tests = db.session.query(LookupBloodTests, LookupBloodTestRanges
                ).filter(LookupBloodTestRanges.modobio_test_code == LookupBloodTests.modobio_test_code
                ).all()
        
        res = []
        for test, range in tests:
            if range.race_id:
                range.race = LookupRaces.query.filter_by(race_id=range.race_id).one_or_none().race_name
            else:
                range.race = None
            res.append({'test': test, 'range': range})
        return {'total_items': len(res), 'items': res}

@ns.route('/developers/')
class LookupDevNamesApi(BaseResource):
    """
    Endpoint that returns development team member names and number of names, in random order
    """
    @token_auth.login_required
    @responds(schema=LookupDevNamesOutputSchema, status_code=200, api=ns)
    def get(self): 
        names = LookupDevNames.query.all()
        
        random.shuffle(names)

        return {'total_items': len(names), 'items': names}
    
    
@ns.route('/visit-reasons/')
@ns.doc(params={'role': 'role for which some of all visit reasons apply'})
class LookupVisitReasonsApi(BaseResource):
    """
    Endpoint that returns visit reasons for all or a specific role
    """
    @token_auth.login_required
    @responds(schema=LookupVisitReasonsOutputSchema, status_code=200, api=ns)
    def get(self):
        role_param = request.args.get('role')

        if role_param == None:
            reasons = LookupVisitReasons.query.all()
        else:
            role = LookupRoles.query.filter_by(role_name = role_param).one_or_none()
            if not role:
                raise BadRequest(f'Role:{role_param} not found.')
            reasons = LookupVisitReasons.query.filter_by(role_id=role.idx).all()

        return {'total_items': len(reasons), 'items': reasons}
