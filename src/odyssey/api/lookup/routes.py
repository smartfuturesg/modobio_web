from flask_accepts import responds
from flask_restx import Resource

from odyssey.api import api
from odyssey.utils.auth import token_auth
from odyssey.api.lookup.models import LookupDrinks, LookupGoalsApi
from odyssey.api.lookup.schemas import LookupDrinksSchema, LookupGoalsSchema

from odyssey import db

ns = api.namespace('lookup', description='Endpoints for lookup tables.')

@ns.route('/drinks/')
class LookupDrinksApi(Resource):
    
    @token_auth.login_required
    @responds(schema=LookupDrinksSchema, api=ns)
    def get(self):
        """get contents of drinks lookup table"""
        return LookupDrinks.query.all()

@ns.route('/drinks/<int:drink_id>')
@ns.doc('Id of the desired drink')
class LookupDrinkIngredientsApi(Resource):

    @token_auth.login_required
    @responds(schema=LookupDrinkIngredientsScehma(many=True))
    def get(self):
        """get recipe of the drink denoted by drink_id"""
        return LookupDrinkIngredients.query.filter_by(drink_id=drink_id).all()

@ns.route('/goals/')
class LookupGoalsApi(Resouce):

    @token_auth.login_required
    @responds(schema=LookupGoalsSchema, api=ns)
    def get(self):
        """get contents of goals lookup table"""
        return LookupGoals.query.all()