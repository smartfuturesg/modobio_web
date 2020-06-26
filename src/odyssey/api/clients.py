
from flask import request, jsonify
from flask_restx import Resource, Api

from odyssey.api import api
from odyssey.api.auth import token_auth, token_auth_client
from odyssey.api.errors import UserNotFound, ClientAlreadyExists, ClientNotFound, IllegalSetting
from odyssey.api.serializers import (
    client_info, 
    client_individual_services_contract,
    client_individual_services_contract_edit,
    client_consent, 
    client_consent_edit, 
    client_release, 
    client_release_edit, 
    initialize_remote_registration,
    pagination,
    refresh_remote_registration,
    remote_registration_reponse,
    sign_and_date,
    sign_and_date_edit
)
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

ns = api.namespace('client', description='Operations related to clients')

@ns.route('/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class Client(Resource):
    @ns.doc(security='apikey')
    @token_auth.login_required
    @ns.marshal_with(client_info)
    def get(self, clientid):
        """returns client info table as a json for the clientid specified"""
        client = ClientInfo.query.get(clientid)
        if not client:
            raise UserNotFound(clientid)
        return client.to_dict()

    @ns.expect(client_info)
    @ns.doc(security='apikey')
    @token_auth.login_required
    @ns.marshal_with(client_info)
    def put(self, clientid):
        """edit client info"""
        # look into changing to .json
        data = request.get_json()
        client = ClientInfo.query.filter_by(clientid=clientid).one_or_none()
        if not client:
            raise UserNotFound(clientid)
        #prevent requests to set clientid and send message back to api user
        elif data.get('clientid', None):
            raise IllegalSetting('clientid')
        # client.update
        client.from_dict(data)
        db.session.add(client)
        db.session.flush()
        db.session.commit()
        return client.to_dict()

@ns.route('/')
class NewClient(Resource):
    """
        create new clients. This is part of the normal flow where clients register on location
    """
    @token_auth.login_required
    @ns.expect(client_info, validate=True)
    @ns.doc(security='apikey')
    @ns.marshal_with(client_info)
    def post(self):
        """create new client"""
        data = request.get_json()
        #make sure this user email does not exist
        if data.get('email', None) and ClientInfo.query.filter_by(email=data.get('email', None)).first():
            raise ClientAlreadyExists(identification = data['email'])
        #prevent requests to set clientid and send message back to api user
        elif data.get('clientid', None):
            raise IllegalSetting('clientid')
        
        client = ClientInfo()
        client.from_dict(data)
        db.session.add(client)
        db.session.flush()
        response = client.to_dict()
        response['__links'] = api.url_for(Client, clientid = client.clientid)
        db.session.commit()
        return response, 201


@ns.route('/clientsearch/', methods=['GET'])
@ns.doc(params={'page': 'request page for paginated clients list', 'per_page': 'number of clients per page'})
class Clients(Resource):
    @ns.doc(security='apikey')
    @ns.expect(pagination)
    @token_auth.login_required
    def get(self):
        """returns list of all clients"""
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        data, resources = ClientInfo.all_clients_dict(ClientInfo.query.order_by(ClientInfo.lastname.asc()),
                                            page=page,per_page=per_page)
        data['_links']= {
            'self': api.url_for(Clients, page=page, per_page=per_page),
            'next': api.url_for(Clients, page=page + 1, per_page=per_page)
            if resources.has_next else None,
            'prev': api.url_for(Clients, page=page - 1, per_page=per_page)
            if resources.has_prev else None,
        }

        return jsonify(data)

@ns.route('/consent/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class ConsentContract(Resource):
    """client consent forms"""
    @ns.doc(security='apikey')
    @token_auth.login_required
    @ns.marshal_with(client_consent)
    def get(self, clientid):
        """returns the most recent consent table as a json for the clientid specified"""
        client_consent_form = ClientConsent.query.filter_by(clientid=clientid).order_by(ClientConsent.signdate.desc()).first()

        if not client_consent_form:
            raise UserNotFound(clientid, message = f"The client with id: {clientid} does not yet have a consultation contract in the database")
        
        return  client_consent_form.to_dict()

    @ns.expect(client_consent_edit)
    @ns.doc(security='apikey')
    @token_auth.login_required
    @ns.marshal_with(client_consent)
    def post(self, clientid):
        """create new client consent contract for the specified clientid"""
        data = request.get_json()
        client_consent_form = ClientConsent()
        client_consent_form.from_dict(clientid, data)
        db.session.add(client_consent_form)
        db.session.flush()
        db.session.commit()
        response = client_consent_form.to_dict()
        # response['__links'] = api.url_for(Client, clientid = clientid) # to add links later on
        return response, 201

    # @ns.expect(client_consent_edit)
    # @ns.doc(security='apikey')
    # @token_auth.login_required
    # @ns.marshal_with(client_consent)
    # def put(self, clientid):
    #     """edit client consent object for the specified clientid"""
    #     data = request.get_json()
    #     client = ClientConsent.query.filter_by(clientid=clientid).one_or_none()
    #     if not client:
    #         raise UserNotFound(clientid)
    #     client.from_dict(clientid, data)
    #     db.session.add(client)
    #     db.session.flush()
    #     db.session.commit()
    #     response = client.to_dict()
    #     # response['__links'] = api.url_for(Client, clientid = clientid) # to add links later on
    #     return response, 201

@ns.route('/release/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class ReleaseContract(Resource):
    """Client release forms"""
    @ns.doc(security='apikey')
    @token_auth.login_required
    @ns.marshal_with(client_release)
    def get(self, clientid):
        """returns most recent client release table as a json for the clientid specified"""
        client_release_form =  ClientRelease.query.filter_by(clientid=clientid).order_by(ClientRelease.signdate.desc()).first()

        if not client_release_form:
            raise UserNotFound(clientid, message = f"The client with id: {clientid} does not yet have a release contract in the database")

        return  client_release_form.to_dict()

    @ns.expect(client_release_edit)
    @ns.doc(security='apikey')
    @token_auth.login_required
    @ns.marshal_with(client_release)
    def post(self, clientid):
        """create client release contract object for the specified clientid"""
        data = request.get_json()
        client_release_form = ClientRelease()
        client_release_form.from_dict(clientid, data)
        db.session.add(client_release_form)
        db.session.flush()
        db.session.commit()
        response = client_release_form.to_dict()
        return response, 201

@ns.route('/policies/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class PoliciesContract(Resource):
    """Client policies form"""

    @ns.doc(security='apikey')
    @token_auth.login_required
    @ns.marshal_with(sign_and_date)
    def get(self, clientid):
        """returns most recent client policies table as a json for the clientid specified"""
        client_policies =  ClientPolicies.query.filter_by(clientid=clientid).order_by(ClientPolicies.signdate.desc()).first()

        if not client_policies:
            raise UserNotFound(clientid, message = f"The client with id: {clientid} does not yet have a policy contract in the database")

        return  client_policies.to_dict()

    @ns.expect(sign_and_date_edit)
    @ns.doc(security='apikey')
    @token_auth.login_required
    @ns.marshal_with(sign_and_date)
    def post(self, clientid):
        """create client policies contract object for the specified clientid"""
        data = request.get_json()
        client_policies = ClientPolicies()
        client_policies.from_dict(clientid, data)
        db.session.add(client_policies)
        db.session.flush()
        db.session.commit()
        response = client_policies.to_dict()
        return response, 201

    # @ns.expect(sign_and_date_edit)
    # @ns.doc(security='apikey')
    # @token_auth.login_required
    # @ns.marshal_with(sign_and_date)
    # def put(self, clientid):
    #     """edit client policies object for the specified clientid"""
    #     data = request.get_json()
    #     client = ClientPolicies.query.filter_by(clientid=clientid).first_or_404()
    #     client.from_dict(clientid, data)
    #     db.session.add(client)
    #     db.session.flush()
    #     db.session.commit()
    #     response = client.to_dict()
    #     # response['__links'] = api.url_for(Client, clientid = clientid) # to add links later on
    #     return response, 201

@ns.route('/consultcontract/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class ConsultConstract(Resource):
    """client consult contract"""

    @ns.doc(security='apikey')
    @token_auth.login_required
    @ns.marshal_with(sign_and_date)
    def get(self, clientid):
        """returns most recent client consultation table as a json for the clientid specified"""
        client_consult =  ClientConsultContract.query.filter_by(clientid=clientid).order_by(ClientConsultContract.signdate.desc()).first()

        if not client_consult:
            raise UserNotFound(clientid, message = f"The client with id: {clientid} does not yet have a consultation contract in the database")

        return  client_consult.to_dict()

    @ns.expect(sign_and_date_edit)
    @ns.doc(security='apikey')
    @token_auth.login_required
    @ns.marshal_with(sign_and_date)
    def post(self, clientid):
        """create client consult contract object for the specified clientid"""
        data = request.get_json()
        client_consult = ClientConsultContract()
        client_consult.from_dict(clientid, data)
        db.session.add(client_consult)
        db.session.flush()
        db.session.commit()
        response = client_consult.to_dict()
        return response, 201

@ns.route('/subscriptioncontract/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class SubscriptionContract(Resource):
    """client subscription contract"""
    @ns.doc(security='apikey')
    @token_auth.login_required
    @ns.marshal_with(sign_and_date)
    def get(self, clientid):
        """returns most recent client subscription contract table as a json for the clientid specified"""
        client_subscription =  ClientSubscriptionContract.query.filter_by(clientid=clientid).order_by(ClientSubscriptionContract.signdate.desc()).first()

        if not client_subscription:
            raise UserNotFound(clientid, message = f"The client with id: {clientid} does not yet have a subscription contract in the database")

        return  client_subscription.to_dict()

    @ns.expect(sign_and_date_edit)
    @ns.doc(security='apikey')
    @token_auth.login_required
    @ns.marshal_with(sign_and_date)
    def post(self, clientid):
        """create client subscription contract object for the specified clientid"""
        data = request.get_json()
        client_subscription = ClientSubscriptionContract()
        client_subscription.from_dict(clientid, data)
        db.session.add(client_subscription)
        db.session.flush()
        db.session.commit()
        response = client_subscription.to_dict()
        return response, 201

@ns.route('/servicescontract/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class IndividualContract(Resource):
    """client individual services contract"""
    @ns.doc(security='apikey')
    @token_auth.login_required
    @ns.marshal_with(client_individual_services_contract)
    def get(self, clientid):
        """returns most recent client individual servies table as a json for the clientid specified"""
        client_services =  ClientIndividualContract.query.filter_by(clientid=clientid).order_by(ClientIndividualContract.signdate.desc()).first()

        if not client_services:
            raise UserNotFound(clientid, message = f"The client with id: {clientid} does not yet have an individual services contract in the database")

        return  client_services.to_dict()

    @ns.expect(client_individual_services_contract_edit)
    @ns.doc(security='apikey')
    @token_auth.login_required
    @ns.marshal_with(client_individual_services_contract)
    def post(self, clientid):
        """create client individual services contract object for the specified clientid"""
        data = request.get_json()
        client_services = ClientIndividualContract()
        client_services.from_dict(clientid, data)
        db.session.add(client_services)
        db.session.flush()
        db.session.commit()
        response = client_services.to_dict()
        return response, 201


@ns.route('/remoteregistration/new/')
class NewRemoteRegistration(Resource):
    """
        initialize a client for remote registration
    """
    @token_auth.login_required
    @ns.expect(initialize_remote_registration, validate=True)
    @ns.doc(security='apikey')
    @ns.marshal_with(remote_registration_reponse)
    def post(self):
        """create new remote registration client
            this will create a new entry into the client info table first
            then create an entry into the Remote registration table
            response includes the hash required to access the temporary portal for 
            this client
        """
        data = request.get_json()

        #make sure this user email does not exist        
        if data.get('email', None) and ClientInfo.query.filter_by(email=data.get('email', None)).first():
            raise ClientAlreadyExists(identification = data['email'])

        # enter client into basic info table and remote register table
        client_info = ClientInfo() 
        remote_client = RemoteRegistration()

        client_info.from_dict(data)
        db.session.add(client_info)
        db.session.flush()
        
        data['clientid'] = client_info.clientid
        remote_client.from_dict(data)
        
        #create temporary passwork and portal url
        pwd = remote_client.set_password(client_info.firstname, client_info.lastname)
        remote_client.get_temp_registration_endpoint()

        db.session.add(remote_client)
        db.session.flush()

        response = remote_client.to_dict()
        response['password'] = pwd
        db.session.commit()
        return response, 201


@ns.route('/remoteregistration/refresh/')
class RefreshRemoteRegistration(Resource):
    """
        refresh client portal a client for remote registration
    """
    @token_auth.login_required
    @ns.expect(refresh_remote_registration, validate=True)
    @ns.doc(security='apikey')
    @ns.marshal_with(remote_registration_reponse)
    def post(self):
        """refresh the portal endpoint and password
        """
        data = request.get_json() #should only need the email

        client_info = ClientInfo.query.filter_by(email=data.get('email', None)).first()

        #if client isnt in the database return error
        if not client_info:
            raise ClientNotFound(identification = data['email'])

        #add clientid to the data object from the current client
        data['clientid'] =  client_info.clientid

        #new remote client session entry
        remote_client = RemoteRegistration()
        remote_client.from_dict(data)

        #new password and registration hash
        pwd = remote_client.set_password(client_info.firstname, client_info.lastname)
        remote_client.get_temp_registration_endpoint()

        db.session.add(remote_client)
        db.session.flush()
        
        response = remote_client.to_dict()
        response['password'] = pwd
        db.session.commit()
        return response, 201

@ns.route('/remoteregistration/clientinfo/<string:tmp_registration>/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class RemoteClientInfo(Resource):
    """
        For getting and altering client info table as a remote client.
        Requires token authorization in addition to a valid portal id (tmp_registration)
    """
    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @ns.marshal_with(client_info)
    def get(self, tmp_registration):
        """returns client info table as a json for the clientid specified"""
        #check portal validity
        if not RemoteRegistration().check_portal_id(tmp_registration):
            raise ClientNotFound(message="Resource does not exist")
        client = ClientInfo.query.filter_by(email=token_auth_client.current_user().email).first()

        return client.to_dict()

    @ns.expect(client_info)
    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @ns.marshal_with(client_info)
    def put(self, tmp_registration):
        """edit client info"""
        #check portal validity
        if not RemoteRegistration().check_portal_id(tmp_registration):
            raise ClientNotFound(message="Resource does not exist")

        data = request.get_json()
        #prevent requests to set clientid and send message back to api user
        if data.get('clientid', None):
            raise IllegalSetting('clientid')
        
        client = ClientInfo.query.filter_by(email=token_auth_client.current_user().email).first()
       
        client.from_dict(data)
        db.session.add(client)
        db.session.flush()
        db.session.commit()
        return client.to_dict()
