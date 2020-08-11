

from flask import request, jsonify, current_app
from flask_accepts import accepts, responds
from flask_restx import Resource, Api

# from odyssey.api.utils import check_client_existence
from odyssey.api import api
from odyssey.api.auth import token_auth, token_auth_client
from odyssey.api.errors import ClientNotFound, ContentNotFound, IllegalSetting
from odyssey import db
from odyssey.models.intake import (
    ClientInfo,
    ClientConsent,
    ClientConsultContract,
    ClientIndividualContract,
    ClientPolicies,
    ClientRelease,
    ClientSubscriptionContract,
    RemoteRegistration
)
from odyssey.models.doctor import MedicalHistory
from odyssey.api.schemas import (
    ClientInfoSchema,
    MedicalHistorySchema
) 


ns = api.namespace('remoteclient', description='Operations related to clients')



@ns.route('/clientinfo/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class RemoteClientInfo(Resource):
    """
        For getting and altering client info table as a remote client.
        Requires token authorization in addition to a valid portal id (tmp_registration)
    """
    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @responds(schema=ClientInfoSchema, api=ns)
    def get(self, tmp_registration):
        """returns client info table as a json for the clientid specified"""
        #check portal validity
        if not RemoteRegistration().check_portal_id(tmp_registration):
            raise ClientNotFound(message="Resource does not exist")

        client = ClientInfo.query.filter_by(email=token_auth_client.current_user().email).first()

        return client

    @accepts(schema=ClientInfoSchema, api=ns)
    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @responds(schema=ClientInfoSchema, api=ns)
    def put(self, tmp_registration):
        """edit client info"""
        #check portal validity
        if not RemoteRegistration().check_portal_id(tmp_registration):
            raise ClientNotFound(message="Resource does not exist")

        data = request.get_json()

        client = ClientInfo.query.filter_by(email=token_auth_client.current_user().email).first()

        client.from_dict(data)
        db.session.add(client)
        db.session.commit()
        return client

@ns.route('/medicalhistory/<int:clientid>/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class MedHistory(Resource):
    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @responds(schema=MedicalHistorySchema, api=ns)
    def get(self, tmp_registration):
        """returns client's medical history as a json for the clientid specified"""
        # check portal validity
        if not RemoteRegistration().check_portal_id(tmp_registration):
            raise ClientNotFound(message="Resource does not exist")

        client = MedicalHistory.query.filter_by(clientid=clientid).first()

        if not client:
            raise ContentNotFound()

        return client
    
    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @accepts(schema=MedicalHistorySchema, api=ns)
    @responds(schema=MedicalHistorySchema, status_code=201, api=ns)
    def post(self, tmp_registration):
        """returns client's medical history as a json for the clientid specified"""
        # check portal validity
        if not RemoteRegistration().check_portal_id(tmp_registration):
            raise ClientNotFound(message="Resource does not exist")

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
    @token_auth_client.login_required
    @accepts(schema=MedicalHistorySchema, api=ns)
    @responds(schema=MedicalHistorySchema, api=ns)
    def put(self, tmp_registration):
        """updates client's medical history as a json for the clientid specified"""
        # check portal validity
        if not RemoteRegistration().check_portal_id(tmp_registration):
            raise ClientNotFound(message="Resource does not exist")


        client_mh = MedicalHistory.query.filter_by(clientid=clientid).first()

        if not client_mh:
            raise UserNotFound(clientid, message = f"The client with id: {clientid} does not yet have a medical history in the database")
        
        # get payload and update the current instance followd by db commit
        data = request.get_json()
       
        data['last_examination_date'] = datetime.strptime(data['last_examination_date'], "%Y-%m-%d")
        
        client_mh.update(data)
        db.session.commit()

        return client_mh