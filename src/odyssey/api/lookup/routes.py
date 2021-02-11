from flask_accepts import responds
from flask_restx import Resource

from odyssey.api import api
from odyssey.utils.auth import token_auth
from odyssey.api.lookup.models import (
     LookupActivityTrackers,
     LookupClientBookingWindow,
     LookupClinicalCareTeamResources,
     LookupCountriesOfOperations,
     LookupDefaultHealthMetrics,
     LookupDrinks, 
     LookupDrinkIngredients, 
     LookupGoals, 
     LookupRaces,
     LookupSubscriptions,
     LookupTelehealthSessionCost,
     LookupTelehealthSessionDuration,
     LookupNotifications
)
from odyssey.api.lookup.schemas import (
    LookupActivityTrackersOutputSchema, 
    LookupClientBookingWindowOutputSchema,
    LookupCountriesOfOperationsOutputSchema,
    LookupDefaultHealthMetricsOutputSchema, 
    LookupDrinksOutputSchema, 
    LookupDrinkIngredientsOutputSchema, 
    LookupGoalsOutputSchema,
    LookupRacesOutputSchema,
    LookupSubscriptionsOutputSchema,
    LookupTelehealthSessionCostOutputSchema,
    LookupTelehealthSessionDurationOutputSchema,
    LookupNotificationsOutputSchema,
    LookupCareTeamResourcesOutputSchema
)
from odyssey.utils.misc import check_drink_existence

from odyssey import db

ns = api.namespace('lookup', description='Endpoints for lookup tables.')


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

@ns.route('/business/booking-window/')
class LookupTelehealthSessionCostResource(Resource):
    """ Returns stored client booking windows in database by GET request.

    Returns
    -------
    dict
        JSON encoded dict.
    """
    @token_auth.login_required
    @responds(schema=LookupClientBookingWindowOutputSchema,status_code=200, api=ns)
    def get(self):
                
        window = LookupClientBookingWindow.query.all()
        
        payload = {'items': window,
                   'total_items': len(window)}

        return payload

@ns.route('/business/session-cost/')
class LookupTelehealthSessionCostResource(Resource):
    """ Returns stored telehealth session cost in database by GET request.

    Returns
    -------
    dict
        JSON encoded dict.
    """
    @token_auth.login_required
    @responds(schema=LookupTelehealthSessionCostOutputSchema,status_code=200, api=ns)
    def get(self):
                
        cost = LookupTelehealthSessionCost.query.all()
        
        payload = {'items': cost,
                   'total_items': len(cost)}

        return payload

@ns.route('/business/session-duration/')
class LookupTelehealthSessionDurationResource(Resource):
    """ Returns stored telehealth session duration in database by GET request.

    Returns
    -------
    dict
        JSON encoded dict.
    """
    @token_auth.login_required
    @responds(schema=LookupTelehealthSessionDurationOutputSchema,status_code=200, api=ns)
    def get(self):
                
        durations = LookupTelehealthSessionDuration.query.all()
        
        payload = {'items': durations,
                   'total_items': len(durations)}

        return payload

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
    Returns available resources that can be shared within clinical care teams
    """
    @token_auth.login_required
    @responds(schema=LookupCareTeamResourcesOutputSchema, api=ns)
    def get(self):
        """get contents of clinical care team resources lookup table"""
        res = LookupClinicalCareTeamResources.query.all()
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
