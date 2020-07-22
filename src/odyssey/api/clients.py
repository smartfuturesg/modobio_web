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
    client_signed_documents,
    pagination,
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
from odyssey.constants import DOCTYPE, DOCTYPE_DOCREV_MAP
from odyssey.pdf import to_pdf

from odyssey.api.schemas import (
    ClientIndividualContractSchema,
    ClientInfoSchema, 
    ClientRemoteRegistrationSchema, 
    NewRemoteRegistrationSchema, 
    RefreshRemoteRegistrationSchema,
    SignAndDateSchema
)
from flask_accepts import accepts, responds

ns = api.namespace('client', description='Operations related to clients')

@ns.route('/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class Client(Resource):
    @ns.doc(security='apikey')
    @token_auth.login_required
    @responds(schema=ClientInfoSchema, api=ns)
    def get(self, clientid):
        """returns client info table as a json for the clientid specified"""
        client = ClientInfo.query.get(clientid)
        if not client:
            raise UserNotFound(clientid)
        return client

    @token_auth.login_required
    @accepts(schema=ClientInfoSchema, api=ns)
    @ns.doc(security='apikey')
    @responds(schema=ClientInfoSchema, api=ns)
    def put(self, clientid):
        """edit client info"""
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
        db.session.commit()
        return client

@ns.route('/')
class NewClient(Resource):
    """
        create new clients. This is part of the normal flow where clients register on location
    """
    @token_auth.login_required
    @accepts(schema=ClientInfoSchema, api=ns)
    @ns.doc(security='apikey')
    @responds(schema=ClientInfoSchema, api=ns, status_code=201)
    def post(self):
        """create new client"""
        data = request.get_json()
 
        #make sure this user email does not exist
        if data.get('email', None) and ClientInfo.query.filter_by(email=data.get('email', None)).first():
            raise ClientAlreadyExists(identification = data['email'])
        #prevent requests to set clientid and send message back to api user
        elif data.get('clientid', None):
            raise IllegalSetting('clientid')
   
        ci_schema = ClientInfoSchema()
        client = ci_schema.load(data)
        db.session.add(client)
        db.session.commit()
        return client


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

    doctype = DOCTYPE.consent
    docrev = DOCTYPE_DOCREV_MAP[doctype]

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
        """ Create or update client consent contract for the specified clientid. """
        query = ClientConsent.query.filter_by(clientid=clientid, revision=self.docrev)
        client_consent_form = query.one_or_none()

        if not client_consent_form:
            client_consent_form = ClientConsent(clientid=clientid, **request.json)
            db.session.add(client_consent_form)
        else:
            query.update(request.json)

        db.session.commit()

        to_pdf(clientid, self.doctype)
        response = client_consent_form.to_dict()
        # response['__links'] = api.url_for(Client, clientid = clientid) # to add links later on
        return response, 201

@ns.route('/release/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class ReleaseContract(Resource):
    """Client release forms"""

    doctype = DOCTYPE.release
    docrev = DOCTYPE_DOCREV_MAP[doctype]

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
        client_release_form = ClientRelease(revision=self.docrev)
        client_release_form.from_dict(clientid, data)
        db.session.add(client_release_form)
        db.session.flush()
        db.session.commit()
        to_pdf(clientid, self.doctype)
        response = client_release_form.to_dict()
        return response, 201

@ns.route('/policies/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class PoliciesContract(Resource):
    """Client policies form"""

    doctype = DOCTYPE.policies
    docrev = DOCTYPE_DOCREV_MAP[doctype]

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
        client_policies = ClientPolicies(revision=self.docrev)
        client_policies.from_dict(clientid, data)
        db.session.add(client_policies)
        db.session.flush()
        db.session.commit()
        to_pdf(clientid, self.doctype)
        response = client_policies.to_dict()
        return response, 201

@ns.route('/consultcontract/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class ConsultConstract(Resource):
    """client consult contract"""

    doctype = DOCTYPE.consult
    docrev = DOCTYPE_DOCREV_MAP[doctype]

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
        client_consult = ClientConsultContract(revision=self.docrev)
        client_consult.from_dict(clientid, data)
        db.session.add(client_consult)
        db.session.flush()
        db.session.commit()
        to_pdf(clientid, self.doctype)
        response = client_consult.to_dict()
        return response, 201

@ns.route('/subscriptioncontract/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class SubscriptionContract(Resource):
    """client subscription contract"""

    doctype = DOCTYPE.subscription
    docrev = DOCTYPE_DOCREV_MAP[doctype]

    @ns.doc(security='apikey')
    @token_auth.login_required
    @responds(schema=SignAndDateSchema, api=ns)
    def get(self, clientid):
        """returns most recent client subscription contract table as a json for the clientid specified"""
        client_subscription =  ClientSubscriptionContract.query.filter_by(clientid=clientid).order_by(ClientSubscriptionContract.signdate.desc()).first()

        if not client_subscription:
            raise UserNotFound(clientid, message = f"The client with id: {clientid} does not yet have a subscription contract in the database")

        return  client_subscription

    @ns.doc(security='apikey')
    @accepts(schema=SignAndDateSchema, api=ns)
    @token_auth.login_required
    @responds(schema=SignAndDateSchema, status_code= 201, api=ns)
    def post(self, clientid):
        """create client subscription contract object for the specified clientid"""
        data = request.get_json()
        client_subscription = ClientSubscriptionContract(revision=self.docrev)
        client_subscription.from_dict(clientid, data)
        db.session.add(client_subscription)
        db.session.commit()
        to_pdf(clientid, self.doctype)
        return client_subscription

@ns.route('/servicescontract/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class IndividualContract(Resource):
    """client individual services contract"""

    doctype = DOCTYPE.individual
    docrev = DOCTYPE_DOCREV_MAP[doctype]

    @ns.doc(security='apikey')
    @token_auth.login_required
    @responds(schema=ClientIndividualContractSchema, api=ns)
    def get(self, clientid):
        """returns most recent client individual servies table as a json for the clientid specified"""
        client_services =  ClientIndividualContract.query.filter_by(clientid=clientid).order_by(ClientIndividualContract.signdate.desc()).first()

        if not client_services:
            raise UserNotFound(clientid, message = f"The client with id: {clientid} does not yet have an individual services contract in the database")

        return  client_services

    @token_auth.login_required
    @accepts(schema=ClientIndividualContractSchema, api=ns)
    @ns.doc(security='apikey')
    @responds(schema=ClientIndividualContractSchema,status_code=201, api=ns)
    def post(self, clientid):
        """create client individual services contract object for the specified clientid"""
        data = request.get_json()
        client_services = ClientIndividualContract(revision=self.docrev)
        client_services.from_dict(clientid, data)
        db.session.add(client_services)
        db.session.commit()
        to_pdf(clientid, self.doctype)
        return client_services

@ns.route('/signeddocuments/<int:clientid>/', methods=('GET',))
@ns.doc(params={'clientid': 'Client ID number'})
class SignedDocuments(Resource):
    """
    API endpoint that provides access to documents signed
    by the client and stored as PDF files.

    Returns
    -------

    Returns a list of URLs where the PDF documents are stored.
    """
    @ns.doc(security='apikey')
    @token_auth.login_required
    @ns.marshal_with(client_signed_documents)
    def get(self, clientid):
        """Given a clientid, returns a list of URLs for all signed documents."""
        client = ClientInfo.query.filter_by(clientid=clientid).one_or_none()

        if not client:
            raise UserNotFound(clientid)

        urls = []

        for table in (ClientPolicies,
                      ClientRelease,
                      ClientConsent,
                      ClientConsultContract,
                      ClientSubscriptionContract,
                      ClientIndividualContract):
            result = table.query.filter_by(clientid=clientid).order_by(table.revision.desc()).first()
            if result and result.url:
                urls.append(result.url)

        return {'urls': urls}

@ns.route('/remoteregistration/new/')
class NewRemoteRegistration(Resource):
    """
        initialize a client for remote registration
    """
    @token_auth.login_required
    @accepts(schema=NewRemoteRegistrationSchema, api=ns)
    @ns.doc(security='apikey')
    @responds(schema=ClientRemoteRegistrationSchema, api=ns, status_code=201)
    def post(self):
        """create new remote registration client
            this will create a new entry into the client info table first
            then create an entry into the Remote registration table
            response includes the hash required to access the temporary portal for
            this client
        """
        data = request.get_json()

        #make sure this user email does not exist
        if ClientInfo.query.filter_by(email=data.get('email', None)).first():
            raise ClientAlreadyExists(identification = data['email'])

        # initialize schema objects
        rr_schema = NewRemoteRegistrationSchema()
        client_rr_schema = ClientRemoteRegistrationSchema()

        # enter client into basic info table and remote register table
        client = rr_schema.load(data)
        
        # add client to database (creates clientid)
        db.session.add(client)
        db.session.flush()

        # create a new remote client registration entry
        remote_client = RemoteRegistration()
        data['clientid'] = client.clientid
        remote_client.from_dict(data)

        # create temporary password and portal url
        remote_client.set_password()
        remote_client.get_temp_registration_endpoint()

        db.session.add(remote_client)
        db.session.commit()

        return remote_client


@ns.route('/remoteregistration/refresh/')
class RefreshRemoteRegistrationSchema(Resource):
    """
        refresh client portal a client for remote registration
    """
    @token_auth.login_required
    @accepts(schema=RefreshRemoteRegistrationSchema)
    @ns.doc(security='apikey')
    @responds(schema=ClientRemoteRegistrationSchema, api=ns, status_code=201)
    def post(self):
        """refresh the portal endpoint and password
        """
        data = request.get_json() #should only need the email

        client = ClientInfo.query.filter_by(email=data.get('email', None)).first()

        #if client isnt in the database return error
        if not client:
            raise ClientNotFound(identification = data['email'])

        #add clientid to the data object from the current client
        data['clientid'] =  client.clientid

        # create a new remote client session registration entry
        remote_client = RemoteRegistration()
        data['clientid'] = client.clientid
        remote_client.from_dict(data)

        # create temporary password and portal url
        remote_client.set_password()
        remote_client.get_temp_registration_endpoint()

        db.session.add(remote_client)
        db.session.commit()

        return remote_client

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
