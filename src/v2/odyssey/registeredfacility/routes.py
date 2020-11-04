from flask import request
from flask_accepts import accepts, responds
from flask_restx import Resource

from odyssey.api import api
from odyssey.utils.auth import token_auth
from odyssey.errors.handlers import ContentNotFound

from odyssey.client.models import ClientFacilities
from odyssey.misc.models import RegisteredFacilities
from odyssey.client.schemas import ClientFacilitiesSchema
from odyssey.staff.schemas import RegisteredFacilitiesSchema
from odyssey.utils.misc import check_facility_existence, check_client_existence, check_client_facility_relation_existence

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

@ns.route('/all/')
class AllFacilities(Resource):
    """api to return all registered facilities in the database"""

    @token_auth.login_required
    @responds(schema=RegisteredFacilitiesSchema(many=True), api=ns)
    def get(self):
        """get a list of all registered facilities"""
        return RegisteredFacilities.query.all()

@ns.route('/')
class NewFacility(Resource):
    """api to create a new registered facility"""

    @token_auth.login_required
    @accepts(schema=RegisteredFacilitiesSchema, api=ns)
    @responds(schema=RegisteredFacilitiesSchema, status_code=201, api=ns)
    def post(self):
        """create a new registered facility"""
        data = request.get_json()

        #prevent requests to set clientid and send message back to api user
        if data.get('facility_id', None):
            raise IllegalSetting('facility_id')

        facility_data = RegisteredFacilitiesSchema().load(data)
        db.session.add(facility_data)
        db.session.commit()
        return facility_data

@ns.route('/client/<int:clientid>/')
class RegisterClient(Resource):
    """api to handle actions revolving around what facilities a client is registered to"""

    @token_auth.login_required
    @responds(schema=RegisteredFacilitiesSchema(many=True), api=ns)
    def get(self, clientid):
        """get list of facilities a client is associated with"""
        check_client_existence(clientid)

        clientFacilities = ClientFacilities.query.filter_by(client_id=clientid).all()

        facilityList = [item.facility_id for item in clientFacilities]

        response = []
        for item in facilityList:
            response.append(RegisteredFacilities.query.filter_by(facility_id=item).first())

        return response

    @token_auth.login_required
    @accepts(schema=ClientFacilitiesSchema, api=ns)
    @responds(schema=ClientFacilitiesSchema, status_code=201, api=ns)
    def post(self, clientid):
        """create a new client-facility relation"""        
        check_client_existence(clientid)
        
        data = request.get_json()

        data['client_id'] = clientid

        check_facility_existence(data['facility_id'])

        #check if this client-facility relation already exists
        check_client_facility_relation_existence(clientid, data['facility_id'])

        facility_data = ClientFacilitiesSchema().load(data)

        db.session.add(facility_data)
        db.session.commit()

        return facility_data