
from datetime import datetime

from flask import request
from flask_accepts import accepts, responds
from flask_restx import Resource, Api

from odyssey import db
from odyssey.models.doctor import MedicalPhysicalExam, MedicalHistory
from odyssey.api import api
from odyssey.api.auth import token_auth
from odyssey.api.schemas import MedicalHistorySchema
from odyssey.api.utils import check_client_existence
from odyssey.api.errors import UserNotFound, IllegalSetting

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




# @bp.route('/doctor/medicalphysicalexam/<int:clientid>/', methods=['GET'])
# @token_auth.login_required
# def get_medical_physical(clientid):
#     """returns medical history for the specified client id"""
#     return MedicalPhysicalExam.query.filter_by(clientid=clientid).first_or_404().to_dict()

