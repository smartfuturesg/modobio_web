
from datetime import datetime

from flask import request
from flask_accepts import accepts, responds
from flask_restx import Resource, Api

from odyssey import db
from odyssey.models.doctor import MedicalPhysicalExam, MedicalHistory
from odyssey.api import api
from odyssey.api.auth import token_auth
from odyssey.api.errors import UserNotFound, IllegalSetting, ContentNotFound
from odyssey.utils.misc import check_client_existence
from odyssey.utils.schemas import MedicalHistorySchema, MedicalPhysicalExamSchema

ns = api.namespace('doctor', description='Operations related to doctor')


@ns.route('/medicalhistory/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class MedHistory(Resource):
    @ns.doc(security='apikey')
    @token_auth.login_required
    @responds(schema=MedicalHistorySchema, api=ns)
    def get(self, clientid):
        """returns client's medical history as a json for the clientid specified"""
        check_client_existence(clientid)

        client = MedicalHistory.query.filter_by(clientid=clientid).first()

        if not client:
            raise ContentNotFound()

        return client
    
    @ns.doc(security='apikey')
    @token_auth.login_required
    @accepts(schema=MedicalHistorySchema, api=ns)
    @responds(schema=MedicalHistorySchema, status_code=201, api=ns)
    def post(self, clientid):
        """returns client's medical history as a json for the clientid specified"""
        check_client_existence(clientid)

        current_med_history = MedicalHistory.query.filter_by(clientid=clientid).first()
        
        if current_med_history:
            raise IllegalSetting(message=f"Medical History for clientid {clientid} already exists. Please use PUT method")


        data = request.get_json()
        data["clientid"] = clientid

        mh_schema = MedicalHistorySchema()

        client_mh = mh_schema.load(data)
        db.session.add(client_mh)
        db.session.commit()

        return client_mh

    @ns.doc(security='apikey')
    @token_auth.login_required
    @accepts(schema=MedicalHistorySchema, api=ns)
    @responds(schema=MedicalHistorySchema, api=ns)
    def put(self, clientid):
        """updates client's medical history as a json for the clientid specified"""
        check_client_existence(clientid)

        client_mh = MedicalHistory.query.filter_by(clientid=clientid).first()

        if not client_mh:
            raise UserNotFound(clientid, message = f"The client with id: {clientid} does not yet have a medical history in the database")
        
        # get payload and update the current instance followd by db commit
        data = request.get_json()
       
        data['last_examination_date'] = datetime.strptime(data['last_examination_date'], "%Y-%m-%d")
        
        client_mh.update(data)
        db.session.commit()

        return client_mh


@ns.route('/physical/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class MedPhysical(Resource):
    @ns.doc(security='apikey')
    @token_auth.login_required
    @responds(schema=MedicalPhysicalExamSchema(many=True), api=ns)
    def get(self, clientid):
        """returns client's medical physical exam as a json for the clientid specified"""
        check_client_existence(clientid)

        client = MedicalPhysicalExam.query.filter_by(clientid=clientid).order_by(MedicalPhysicalExam.timestamp.asc()).all()

        if not client:
            raise ContentNotFound()

        return client
    
    @ns.doc(security='apikey')
    @token_auth.login_required
    @accepts(schema=MedicalPhysicalExamSchema, api=ns)
    @responds(schema=MedicalPhysicalExamSchema, status_code=201, api=ns)
    def post(self, clientid):
        """creates new db entry of client's medical physical exam as a json for the clientid specified"""
        check_client_existence(clientid)

        data = request.get_json()
        data["clientid"] = clientid
        data["timestamp"] = datetime.utcnow().isoformat()

        mh_schema = MedicalPhysicalExamSchema()

        client_mp = mh_schema.load(data)

        db.session.add(client_mp)
        db.session.commit()

        return client_mp

    # @ns.doc(security='apikey')
    # @token_auth.login_required
    # @accepts(schema=MedicalPhysicalExamSchema, api=ns)
    # @responds(schema=MedicalPhysicalExamSchema, api=ns)
    # def put(self, clientid):
    #     """updates client's medical physical exam as a json for the clientid specified"""
    #     check_client_existence(clientid)

    #     client_mp = MedicalPhysicalExam.query.filter_by(clientid=clientid).first()

    #     if not client_mp:
    #         raise UserNotFound(clientid, message = f"The client with id: {clientid} does not yet have a medical physical exam in the database")
        
    #     # get payload and update the current instance followd by db commit
    #     data = request.get_json()
       
        
    #     client_mp.update(data)
    #     db.session.commit()

    #     return client_mp





