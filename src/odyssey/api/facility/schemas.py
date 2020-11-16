from marshmallow import Schema, fields, post_load

from odyssey import ma
from odyssey.api.user.models import User
from odyssey.api.facility.models import RegisteredFacilities

class RegisteredFacilitiesSchema(Schema):
    facility_id = fields.Integer(required=False)
    facility_name = fields.String(required=True)
    facility_address = fields.String(required=True)
    modobio_facility = fields.Boolean(required=True)

    @post_load
    def make_object(self, data, **kwargs):
        return RegisteredFacilities(**data)

class ClientSummarySchema(Schema):

    firstname = fields.String()
    middlename = fields.String()
    lastname = fields.String()
    dob = fields.Date()
    user_id = fields.Integer()
    membersince = fields.Date()
    facilities = fields.Nested(RegisteredFacilitiesSchema(many=True))
