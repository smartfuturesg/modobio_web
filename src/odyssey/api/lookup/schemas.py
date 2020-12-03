from marshmallow import Schema, fields, post_load

from odyssey import ma
from odyssey.api.lookup.models import LookupDrinks, LookupDrinkIngredients, LookupGoals

class LookupDrinksSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupDrinks
        exclude = ('created_at', 'updated_at')

    primary_ingredient = fields.String()
    goal = fields.String()

    @post_load
    def make_object(self, data, **kwargs):
        return LookupDrinks(**data)

class LookupDrinkIngredientsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupDrinkIngredients
        exclude = ('idx', 'created_at', 'updated_at')

    @post_load
    def make_object(self, data, **kwargs):
        return LookupDrinkIngredients(**data)

class LookupGoalsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupGoals
        exclude = ('created_at', 'updated_at')

    @post_load
    def make_object(self, data, **kwargs):
        return LookupGoals(**data)