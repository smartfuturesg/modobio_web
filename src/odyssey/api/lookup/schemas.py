from marshmallow import Schema, post_load

from odyssey import ma
from odyssey.api.lookup.models import LookupDrinks, LookupGoals

class LookupDrinksSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupDrinks
        exclude = ('idx', 'created_at', 'updated_at')

    @post_load
    def make_object(self, data, **kwargs):
        return LookupDrinks(**data)

class LookupGoalsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LookupDrinks
        exclude = ('idx', 'created_at', 'updated_at')

    @post_load
    def make_object(self, data, **kwargs):
        return LookupGoals(**data)