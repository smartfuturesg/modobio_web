
from datetime import datetime

from flask import request, jsonify
from flask_restx import Resource, Api
from flask_accepts import accepts, responds

from odyssey.api.utils import check_client_existence
from odyssey.api import api
from odyssey.api.auth import token_auth, token_auth_client
from odyssey.api.errors import UserNotFound, ClientAlreadyExists, ClientNotFound, IllegalSetting
from odyssey.api.schemas import (
    ClientInfoSchema,
    HeartAssessmentSchema,
    PowerAssessmentSchema,
    StrenghtAssessmentSchema,
    MovementAssessmentSchema,
    MoxyAssessmentSchema
)
from odyssey import db
from odyssey.models.trainer import (
    HeartAssessment,
    PowerAssessment,
    StrengthAssessment,
    MovementAssessment,
    MoxyAssessment
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
    @responds(schema=PowerAssessmentSchema, status_code=201, api=ns)
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
    @responds(schema=StrenghtAssessmentSchema, status_code=201, api=ns)
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


@ns.route('/assessment/movement/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class Movement(Resource):

    """GET and POST movement assessments for the client"""

    @ns.doc(security='apikey')
    @token_auth.login_required
    @responds(schema=MovementAssessmentSchema(many=True), api=ns)
    def get(self, clientid):
        """returns all power assessment entries for the specified client"""
        check_client_existence(clientid)

        all_entries = MovementAssessment.query.filter_by(clientid=clientid).order_by(MovementAssessment.timestamp.asc()).all()

        if len(all_entries) == 0:
            raise UserNotFound(
                clientid=clientid, 
                message = "this client does not yet have a power assessment")
        
        return all_entries

    @ns.doc(security='apikey')
    @token_auth.login_required
    @accepts(schema=MovementAssessmentSchema, api=ns)
    @responds(schema=MovementAssessmentSchema, status_code=201, api=ns)
    def post(self, clientid):
        """create a power assessment entry for clientid"""
        check_client_existence(clientid)

        data=request.get_json()
        data['clientid'] = clientid

        sa_schema = MovementAssessmentSchema()
        client_sa = sa_schema.load(data)

        db.session.add(client_sa)
        db.session.commit()
        
        most_recent = MovementAssessment.query.filter_by(clientid=clientid).order_by(MovementAssessment.timestamp.desc()).first()
        return most_recent

@ns.route('/assessment/heart/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class Heart(Resource):
    
    """GET and POST movement assessments for the client"""

    @ns.doc(security='apikey')
    @token_auth.login_required
    @responds(schema=HeartAssessmentSchema(many=True), api=ns)
    def get(self, clientid):
        """returns all power assessment entries for the specified client"""
        check_client_existence(clientid)

        all_entries = HeartAssessment.query.filter_by(clientid=clientid).order_by(HeartAssessment.timestamp.asc()).all()

        if len(all_entries) == 0:
            raise UserNotFound(
                clientid=clientid, 
                message = "this client does not yet have a power assessment")
        
        return all_entries

    @ns.doc(security='apikey')
    @token_auth.login_required
    @accepts(schema=HeartAssessmentSchema, api=ns)
    @responds(schema=HeartAssessmentSchema, status_code=201, api=ns)
    def post(self, clientid):
        """create a power assessment entry for clientid"""
        check_client_existence(clientid)

        data=request.get_json()
        data['clientid'] = clientid
        data['timestamp'] = datetime.utcnow().isoformat()

        hr_schema = HeartAssessmentSchema()
        client_hr = hr_schema.load(data)
        db.session.add(client_hr)
        db.session.commit()
        
        return client_hr

    
@ns.route('/assessment/moxy/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class Moxy(Resource):    
    """GET and POST moxy assessments for the client"""

    @ns.doc(security='apikey')
    @token_auth.login_required
    @responds(schema=MoxyAssessmentSchema(many=True), api=ns)
    def get(self, clientid):
        """returns all power assessment entries for the specified client"""
        check_client_existence(clientid)

        all_entries = MoxyAssessment.query.filter_by(clientid=clientid).order_by(MoxyAssessment.timestamp.asc()).all()

        if len(all_entries) == 0:
            raise UserNotFound(
                clientid=clientid, 
                message = "this client does not yet have a moxy assessment")
        
        return all_entries

    @ns.doc(security='apikey')
    @token_auth.login_required
    @accepts(schema=MoxyAssessmentSchema, api=ns)
    @responds(schema=MoxyAssessmentSchema, status_code=201, api=ns)
    def post(self, clientid):
        """create a power assessment entry for clientid"""
        check_client_existence(clientid)

        data=request.get_json()
        data['clientid'] = clientid
        data['timestamp'] = datetime.utcnow().isoformat()

        moxy_schema = MoxyAssessmentSchema()
        client_moxy = moxy_schema.load(data)
        db.session.add(client_moxy)
        db.session.commit()
        
        return client_moxy

