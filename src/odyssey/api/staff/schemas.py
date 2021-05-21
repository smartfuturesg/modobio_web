from marshmallow import Schema, fields, post_load, validate
from sqlalchemy.orm import load_only
from odyssey import ma
from odyssey.api.user.models import User
from odyssey.api.staff.models import(
    StaffOperationalTerritories, 
    StaffProfile, 
    StaffRoles, 
    StaffRecentClients, 
    StaffCalendarEvents
) 
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

    idx = fields.Integer()
    user_id = fields.Integer()
    possible_roles = ACCESS_ROLES

    @post_load
    def make_object(self, data, **kwargs):
        return StaffProfile(**data)

class StaffRolesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = StaffRoles
        exclude = ('created_at', 'updated_at', 'idx', 'verified')
        include_fk = True
        load_only = ('user_id',)
    role_id = fields.Integer(attribute="idx", dump_only=True)

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
    recurrence_type = fields.String(validate=validate.OneOf(RECURRENCE_TYPE))
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

class StaffCalendarEventsGetSchema(Schema):
    year = fields.Integer(required=False)
    month = fields.Integer(validate=validate.Range(min=1, max=12, min_inclusive=True, max_inclusive=True), required=False)
    day = fields.Integer(validate=validate.Range(min=1, max=31, min_inclusive=True, max_inclusive=True), required=False)