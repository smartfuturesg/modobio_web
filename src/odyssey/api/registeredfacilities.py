from datetime import datetime, timedelta

from flask import current_app, request, url_for
from flask_accepts import accepts, responds
from flask_restx import Resource
from requests_oauthlib import OAuth2Session

from odyssey.api import api
from odyssey.api.auth import token_auth
from odyssey.api.errors import ContentNotFound

from odyssey.models.client import ClientFacilities
from odyssey.models.misc import RegisteredFacilities
from odyssey.utils.schemas import RegisteredFacilitiesSchema, ClientFacilitiesSchema
from odyssey.utils.misc import check_facility_existence, check_client_existence

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

@ns.route('/client/<int:clientid>/')
class RegisterClient(Resource):
    """api to handle actions revolving around what facilities a client is registered to"""

    @token_auth.login_required
    @responds(schema=RegisteredFacilitiesSchema(many=True), api=ns)
    def get(self, clientid):
        """get list of facilities a client is associated with"""
        check_client_existence(clientid)

        clientFacilities = ClientFacilities.query.filter_by(client_id=clientid).all()

        if not clientFacilities:
            raise ContentNotFound()

#       facilities = RegisteredFacilities.query.filter_by(clientid=clientid).all()

#        if not facilities:
#            raise ContentNotFound()

        return clientFacilities

    @token_auth.login_required
    @accepts(schema=ClientFacilitiesSchema, api=ns)
    @responds(schema=ClientFacilitiesSchema, status_code=201, api=ns)
    def post(self, clientid):
        """create a new client-facility relation"""        
        check_client_existence(clientid)
        
        data = request.get_json()

        data['client_id'] = clientid

        check_facility_existence(data['facility_id'])

        facility_schema = ClientFacilitiesSchema()

        facility_data = facility_schema.load(data)

        db.session.add(facility_data)
        db.session.commit()

        return facility_data