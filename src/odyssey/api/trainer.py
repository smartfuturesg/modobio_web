from flask import request, jsonify
from flask_restx import Resource, Api
from flask_accepts import accepts, responds

from odyssey.api.utils import check_client_existence
from odyssey.api import api
from odyssey.api.auth import token_auth, token_auth_client
from odyssey.api.errors import UserNotFound, ClientAlreadyExists, ClientNotFound, IllegalSetting
from odyssey.api.schemas import (
    ClientInfoSchema,
    PowerAssessmentSchema,
    StrenghtAssessmentSchema
)
from odyssey import db
from odyssey.models.trainer import (
    PowerAssessment,
    StrengthAssessment
)

ns = api.namespace('trainer', description='Operations related to the trainer')

@ns.route('/assessment/power/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class Power(Resource):
    """GET and POST power assessments for the client"""

    @ns.doc(security='apikey')
    @token_auth.login_required
    @responds(schema=PowerAssessmentSchema(many=True), api=ns)
    def get(self, clientid):
        """returns all power assessment entries for the specified client"""
        check_client_existence(clientid)

        all_entries = PowerAssessment.query.filter_by(clientid=clientid).order_by(PowerAssessment.timestamp.asc()).all()

        if len(all_entries) == 0:
            raise UserNotFound(
                clientid=clientid, 
                message = "this client does not yet have a power assessment")
        
        return all_entries

    @ns.doc(security='apikey')
    @token_auth.login_required
    @accepts(schema=PowerAssessmentSchema, api=ns)
    @responds(schema=PowerAssessmentSchema, api=ns)
    def post(self, clientid):
        """create a power assessment entry for clientid"""
        check_client_existence(clientid)

        data=request.get_json()
        data['clientid'] = clientid

        pa_schema = PowerAssessmentSchema()
        client_pa = pa_schema.load(data)

        db.session.add(client_pa)
        db.session.commit()

        most_recent =  PowerAssessment.query.filter_by(clientid=clientid).order_by(PowerAssessment.timestamp.desc()).first()
        return most_recent

@ns.route('/assessment/strength/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class Strength(Resource):
    """GET and POST strength assessments for the client"""

    @ns.doc(security='apikey')
    @token_auth.login_required
    @responds(schema=StrenghtAssessmentSchema(many=True), api=ns)
    def get(self, clientid):
        """returns all power assessment entries for the specified client"""
        check_client_existence(clientid)

        all_entries = StrengthAssessment.query.filter_by(clientid=clientid).order_by(StrengthAssessment.timestamp.asc()).all()

        if len(all_entries) == 0:
            raise UserNotFound(
                clientid=clientid, 
                message = "this client does not yet have a power assessment")
        
        return all_entries

    @ns.doc(security='apikey')
    @token_auth.login_required
    @accepts(schema=StrenghtAssessmentSchema, api=ns)
    @responds(schema=StrenghtAssessmentSchema, api=ns)
    def post(self, clientid):
        """create a power assessment entry for clientid"""
        check_client_existence(clientid)

        data=request.get_json()
        data['clientid'] = clientid

        sa_schema = StrenghtAssessmentSchema()
        client_sa = sa_schema.load(data)
        
        db.session.add(client_sa)
        db.session.commit()
        
        most_recent = StrengthAssessment.query.filter_by(clientid=clientid).order_by(StrengthAssessment.timestamp.desc()).first()
        return most_recent
