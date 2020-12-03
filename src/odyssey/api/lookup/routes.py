from flask_accepts import responds
from flask_restx import Resource

from odyssey.api import api
from odyssey.utils.auth import token_auth
from odyssey.api.lookup.models import LookupDrinks, LookupDrinkIngredients, LookupGoals
from odyssey.api.lookup.schemas import LookupDrinksSchema, LookupDrinkIngredientsSchema, LookupGoalsSchema

from odyssey import db

ns = api.namespace('lookup', description='Endpoints for lookup tables.')

@ns.route('/drinks/')
class LookupDrinksApi(Resource):
    
    @token_auth.login_required
    @responds(schema=LookupDrinksSchema(many=True), api=ns)
    def get(self):
        """get contents of drinks lookup table"""
        res = []
        for drink in LookupDrinks.query.all():
            drink.primary_ingredient = LookupDrinkIngredients.query.filter_by(drink_id=drink.drink_id).filter_by(is_primary_ingredient=True).first().ingredient_name
            drink.goal = LookupGoals.query.filter_by(goal_id=drink.primary_goal_id).first().goal_name
            res.append(drink)
        return res

@ns.route('/drinks/ingredients/<int:drink_id>/')
@ns.doc('Id of the desired drink')
class LookupDrinkIngredientsApi(Resource):

    @token_auth.login_required
    @responds(schema=LookupDrinkIngredientsSchema(many=True), api=ns)
    def get(self, drink_id):
        """get recipe of the drink denoted by drink_id"""
        return LookupDrinkIngredients.query.filter_by(drink_id=drink_id).all()

@ns.route('/goals/')
class LookupGoalsApi(Resource):

    @token_auth.login_required
    @responds(schema=LookupGoalsSchema(many=True), api=ns)
    def get(self):
        """get contents of goals lookup table"""
        return LookupGoals.query.all()