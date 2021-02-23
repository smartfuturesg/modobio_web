from marshmallow import Schema, fields, post_load

from odyssey import ma
from odyssey.api.lookup.models import LookupDrinks, LookupDrinkIngredients, LookupGoals, LookupRaces

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