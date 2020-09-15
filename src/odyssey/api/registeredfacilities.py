from datetime import datetime, timedelta

from flask import current_app, request, url_for
from flask_accepts import accepts, responds
from flask_restx import Resource
from requests_oauthlib import OAuth2Session

from odyssey.api import api
from odyssey.api.auth import token_auth
from odyssey.api.errors import ContentNotFound

from odyssey.models.misc import RegisteredFacilities
from odyssey.utils.schemas import RegisteredFacilitiesSchema
from odyssey.utils.misc import check_facility_existence

from odyssey import db

ns = api.namespace('registeredfacility', description='Endpoints for registered facilities.')

@ns.route('/<int:facility_id>/')
class RegisteredFacility(Resource):
    
    @token_auth.login_required
    @responds(schema=RegisteredFacilitiesSchema, api=ns)
    def get(self, facility_id):
        """get registered facility info"""
        check_facility_existence(facility_id)

        facility = RegisteredFacilities.query.filter_by(facility_id=facility_id).first()

        if not facility:
            raise ContentNotFound()

        return facility

    @token_auth.login_required
    @accepts(schema=RegisteredFacilitiesSchema, api=ns)
    @responds(schema=RegisteredFacilitiesSchema, status_code=201, api=ns)
    def post(self, facility_id):
        """create a new registered facility"""
        #facility = RegisteredFacilities.query.filter_by(facility_id=facility_id).first()
        

        data = request.get_json()

        data['facility_id'] = facility_id

        facility_schema = RegisteredFacilitiesSchema()

        facility_data = facility_schema.load(data)

        db.session.add(facility_data)
        db.session.commit()

        return facility_data

    @token_auth.login_required
    @accepts(schema=RegisteredFacilitiesSchema, api=ns)
    @responds(schema=RegisteredFacilitiesSchema, api=ns)
    def put(self, facility_id):
        """edit registered facility info"""

        check_facility_existence(facility_id)

        facility = RegisteredFacilities.query.filter_by(facility_id=facility_id).first()

        data = request.get_json()

        data['facility_id'] = facility_id

        facility.update(data)

        db.session.commit()

        return facility