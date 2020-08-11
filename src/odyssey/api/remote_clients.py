from datetime import datetime

from flask import request, jsonify, current_app
from flask_accepts import accepts, responds
from flask_restx import Resource, Api

from odyssey.api import api
from odyssey.api.auth import token_auth, token_auth_client
from odyssey.api.errors import ClientNotFound, ContentNotFound, IllegalSetting, UserNotFound
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
from odyssey.models.pt import PTHistory
from odyssey.utils.schemas import (
    ClientInfoSchema,
    MedicalHistorySchema,
    PTHistorySchema
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
    def get(self):
        """returns client info table as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')

        # bring up the valid remote client. Returns None is portal is expired 
        remote_client = RemoteRegistration().check_portal_id(tmp_registration)

        # check portal validity
        if not remote_client:
            raise ClientNotFound(message="Resource does not exist")

        client = ClientInfo.query.filter_by(clientid=remote_client.clientid).first()

        return client

    @accepts(schema=ClientInfoSchema, api=ns)
    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @responds(schema=ClientInfoSchema, api=ns)
    def put(self):
        """edit client info"""
        tmp_registration = request.args.get('tmp_registration')
        #check portal validity
        if not RemoteRegistration().check_portal_id(tmp_registration):
            raise ClientNotFound(message="Resource does not exist")

        data = request.get_json()

        client = ClientInfo.query.filter_by(email=token_auth_client.current_user().email).first()

        client.from_dict(data)
        db.session.add(client)
        db.session.commit()
        return client

@ns.route('/medicalhistory/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class MedHistory(Resource):
   
    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @responds(schema=MedicalHistorySchema, api=ns)
    def get(self):
        """returns client's medical history as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')

        remote_client = RemoteRegistration().check_portal_id(tmp_registration)
        # check portal validity
        if not remote_client:
            raise ClientNotFound(message="Resource does not exist")
        
        client_mh = MedicalHistory.query.filter_by(clientid=remote_client.clientid).first()

        if not client_mh:
            raise ContentNotFound()

        return client_mh
    
    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @accepts(schema=MedicalHistorySchema, api=ns)
    @responds(schema=MedicalHistorySchema, status_code=201, api=ns)
    def post(self):
        """creates client's medical history and returns it as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')
        # bring up the valid remote client. Returns None is portal is expired 
        remote_client = RemoteRegistration().check_portal_id(tmp_registration)
       
        # check portal validity
        if not remote_client:
            raise ClientNotFound(message="Resource does not exist")

        current_med_history = MedicalHistory.query.filter_by(clientid=remote_client.clientid).first()
        
        if current_med_history:
            raise IllegalSetting(message=f"Medical History for clientid {remote_client.clientid} already exists. Please use PUT method")

        data = request.get_json()
        data["clientid"] = remote_client.clientid

        mh_schema = MedicalHistorySchema()

        client_mh = mh_schema.load(data)

        db.session.add(client_mh)
        db.session.commit()

        return client_mh

    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @accepts(schema=MedicalHistorySchema, api=ns)
    @responds(schema=MedicalHistorySchema, api=ns)
    def put(self):
        """updates client's medical history as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')

        remote_client = RemoteRegistration().check_portal_id(tmp_registration)
       
        # check portal validity
        if not remote_client:
            raise ClientNotFound(message="Resource does not exist")

        client_mh = MedicalHistory.query.filter_by(clientid=remote_client.clientid).first()

        if not client_mh:
            raise UserNotFound(remote_client.clientid, message = f"The client with id: {remote_client.clientid} does not yet have a medical history in the database")
        
        # get payload and update the current instance followd by db commit
        data = request.get_json()
       
        data['last_examination_date'] = datetime.strptime(data['last_examination_date'], "%Y-%m-%d")
        
        client_mh.update(data)
        db.session.commit()

        return client_mh


@ns.route('/pthistory/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class ClientPTHistory(Resource):
    """GET, POST, PUT for pt history data"""
    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @responds(schema=PTHistorySchema)
    def get(self):
        """returns most recent mobility assessment data"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = RemoteRegistration().check_portal_id(tmp_registration)

        client_pt = PTHistory.query.filter_by(clientid=remote_client.clientid).first()

        if not client_pt:
            raise ContentNotFound() 
                
        return client_pt

    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @accepts(schema=PTHistorySchema, api=ns)
    @responds(schema=PTHistorySchema, status_code=201, api=ns)
    def post(self):
        """returns most recent mobility assessment data"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = RemoteRegistration().check_portal_id(tmp_registration)


        #check to see if there is already an entry for pt history
        current_pt_history = PTHistory.query.filter_by(clientid=remote_client.clientid).first()
        if current_pt_history:
            raise IllegalSetting(message=f"PT History for clientid {remote_client.clientid} already exists. Please use PUT method")

        data = request.get_json()
        data['clientid'] = remote_client.clientid
        
        pth_schema = PTHistorySchema()

        #create a new entry into the pt history table
        client_pt = pth_schema.load(data)

        db.session.add(client_pt)
        db.session.commit()

        return client_pt

    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @accepts(schema=PTHistorySchema, api=ns)
    @responds(schema=PTHistorySchema, api=ns)
    def put(self):
        """edit user's pt history"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = RemoteRegistration().check_portal_id(tmp_registration)


        #check to see if there is already an entry for pt history
        current_pt_history = PTHistory.query.filter_by(
                        clientid=remote_client.clientid).first()

        if not current_pt_history:
            raise UserNotFound(clientid, message = f"The client with id: {remote_client.clientid} does not yet have a pt history in the database")

        
        # get payload and update the current instance followd by db commit
        data = request.get_json()

        current_pt_history.update(data)
        db.session.commit()

        return client_pt