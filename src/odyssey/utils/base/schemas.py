from odyssey import ma

"""
Base schema for the majority of schemas that want to exlucde created_at, updated_at, and idx.

If you do not wish to exclude all of these, do not inherit this schema
"""
class BaseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        exclude = ('created_at', 'updated_at', 'idx')