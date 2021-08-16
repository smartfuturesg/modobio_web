from marshmallow import Schema, fields, post_load, validate
from sqlalchemy.orm import load_only
from odyssey import ma
from odyssey.api.user.models import User
from odyssey.api.staff.models import(
    StaffOperationalTerritories, 
    StaffProfile, 
    StaffRoles, 
    StaffRecentClients, 
    StaffCalendarEvents,
    StaffOffices
) 
from odyssey.utils.base.schemas import BaseSchema
from odyssey.utils.constants import ACCESS_ROLES, EVENT_AVAILABILITY, BOOKINGS_STATUS, RECURRENCE_TYPE

"""
    Schemas for the staff API
"""

class StaffRecentClientsSchema(Schema):
    idx = fields.Integer()
    user_id = fields.Integer()
    client_user_id = fields.Integer(required=True)
    timestamp = fields.DateTime()

    @post_load
    def make_object(self, data, **kwargs):
        return StaffRecentClients(**data)

class StaffSearchItemsSchema(Schema):
    user_id = fields.Integer()
    firstname = fields.String(required=False, validate=validate.Length(min=1, max= 50), missing=None)
    lastname = fields.String(required=False, validate=validate.Length(min=1,max=50), missing=None)
    email = fields.Email(required=False, missing=None)   

class StaffProfileSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = StaffProfile

    user_id = fields.Integer()
    possible_roles = ACCESS_ROLES

    @post_load
    def make_object(self, data, **kwargs):
        return StaffProfile(**data)

class StaffProfilePageGetSchema(Schema):
    firstname = fields.String()
    middlename = fields.String()
    lastname = fields.String()
    biological_sex_male = fields.Boolean()
    profile_picture = fields.Dict(keys=fields.Str(), values=fields.Str())
    bio = fields.String(validate=validate.Length(min=1, max= 50))

class StaffRolesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = StaffRoles
        exclude = ('created_at', 'updated_at', 'idx')
        include_fk = True
        load_only = ('user_id',)
    role_id = fields.Integer(attribute="idx", dump_only=True)
    granter_id = fields.Integer(load_only=True)

    @post_load
    def make_object(self, data, **kwargs):
        return StaffRoles(**data)

class StaffTokenRequestSchema(Schema):
    user_id = fields.Integer()
    firstname = fields.String(required=False, validate=validate.Length(min=1, max= 50), missing=None)
    lastname = fields.String(required=False, validate=validate.Length(min=1,max=50), missing=None)
    email = fields.Email(required=False, missing=None)   
    token = fields.String()
    refresh_token = fields.String()
    access_roles = fields.List(fields.String)
    email_required = fields.Boolean()
     
class StaffOperationalTerritoriesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = StaffOperationalTerritories
        exclude = ('created_at', 'updated_at', 'idx')
        include_fk = True
        dump_only = ('user_id')

    user_id = fields.Integer(missing=None)
    @post_load
    def make_object(self, data, **kwargs):
        return StaffOperationalTerritories(**data)

class StaffOperationalTerritoriesNestedSchema(Schema):
    operational_territories = fields.Nested(StaffOperationalTerritoriesSchema(many=True))

class StaffCalendarEventsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = StaffCalendarEvents
        exclude = ('created_at', 'updated_at')
        dump_only = ('idx', 'user_id', 'duration', 'warning', 'timezone')
        include_fk = True

    availability_status = fields.String(validate=validate.OneOf(EVENT_AVAILABILITY), missing='Available')
    recurrence_type = fields.String(required=False, validate=validate.OneOf(RECURRENCE_TYPE))
    all_day = fields.Boolean(missing=True)
    recurring = fields.Boolean(missing=False)
    warning = fields.String()

    @post_load
    def make_object(self, data, **kwargs):
        return StaffCalendarEvents(**data)

class StaffCalendarEventsUpdateSchema(Schema):
    revised_event_schema = fields.Nested(StaffCalendarEventsSchema(), required=True)
    event_to_update_idx = fields.Integer(required=True)
    entire_series = fields.Boolean(missing=False)
    previous_start_date = fields.Date(required=True)

class StaffOfficesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = StaffOffices
        exclude = ('created_at', 'updated_at', 'idx')

    territory_id = fields.Integer()
    country = fields.String(dump_only=True)
    territory = fields.String(dump_only=True)
    territory_abbreviation = fields.String(dump_only=True)
    phone_type = fields.String(validate=validate.OneOf(('primary', 'cell', 'work', 'home', 'fax', 'night', 'beeper')))

    @post_load
    def make_object(self, data, **kwargs):
        return StaffOffices(**data)