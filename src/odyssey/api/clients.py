import boto3
from datetime import datetime

from flask import request, jsonify
from flask_accepts import accepts, responds, current_app
from flask_restx import Resource, Api

from odyssey.api.utils import check_client_existence
from odyssey.api import api
from odyssey.api.auth import token_auth, token_auth_client
from odyssey.api.errors import UserNotFound, ClientAlreadyExists, ClientNotFound, IllegalSetting, ContentNotFound
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
from odyssey.models.main import ClientRemovalRequests
from odyssey.constants import DOCTYPE, DOCTYPE_DOCREV_MAP
from odyssey.pdf import to_pdf
from odyssey.api.schemas import (
    ClientConsentSchema,
    ClientConsultContractSchema,
    ClientIndividualContractSchema,
    ClientInfoSchema,
    ClientPoliciesContractSchema, 
    ClientReleaseSchema,
    ClientRemoteRegistrationSchema, 
    ClientSubscriptionContractSchema,
    NewRemoteRegistrationSchema, 
    RefreshRemoteRegistrationSchema,
    SignAndDateSchema,
    SignedDocumentsSchema
)


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

@ns.route('/remove/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class RemoveClient(Resource):
    @ns.doc(security='apikey')
    @token_auth.login_required
    def delete(self, clientid):
        """deletes client from database entirely"""
        client = ClientInfo.query.get(clientid)

        if not client:
            raise UserNotFound(clientid)
        
        # find the staff member requesting client delete
        staff = token_auth.current_user()
        new_removal_request = ClientRemovalRequests(staffid=staff.staffid, timestamp=datetime.utcnow())
        
        db.session.add(new_removal_request)
        db.session.flush()

        #TODO: some logic on who gets to delete clients+ email to staff admin
        db.session.delete(client)
        db.session.commit()
        
        return {'message': f'client with id {clientid} has been removed'}

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
    @responds(schema=ClientConsentSchema, api=ns)
    def get(self, clientid):
        """returns the most recent consent table as a json for the clientid specified"""
        check_client_existence(clientid)

        client_consent_form = ClientConsent.query.filter_by(clientid=clientid).order_by(ClientConsent.idx.desc()).first()
        
        if not client_consent_form:
            raise ContentNotFound()

        return client_consent_form

    @accepts(schema=ClientConsentSchema, api=ns)
    @ns.doc(security='apikey')
    @token_auth.login_required
    @responds(schema=ClientConsentSchema, status_code=201, api=ns)
    def post(self, clientid):
        """ Create client consent contract for the specified clientid """
        check_client_existence(clientid)

        data = request.get_json()
        data["clientid"] = clientid

        client_consent_schema = ClientConsentSchema()
        client_consent_form = client_consent_schema.load(data)
        
        db.session.add(client_consent_form)
        db.session.commit()

        to_pdf(clientid, self.doctype)
        return client_consent_form

@ns.route('/release/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class ReleaseContract(Resource):
    """Client release forms"""

    doctype = DOCTYPE.release
    docrev = DOCTYPE_DOCREV_MAP[doctype]

    @ns.doc(security='apikey')
    @token_auth.login_required
    @responds(schema=ClientReleaseSchema, api=ns)
    def get(self, clientid):
        """returns most recent client release table as a json for the clientid specified"""
        check_client_existence(clientid)

        client_release_form =  ClientRelease.query.filter_by(clientid=clientid).order_by(ClientRelease.idx.desc()).first()

        if not client_release_form:
            raise ContentNotFound()

        return client_release_form

    @accepts(schema=ClientReleaseSchema)
    @ns.doc(security='apikey')
    @token_auth.login_required
    @responds(schema=ClientReleaseSchema, status_code=201, api=ns)
    def post(self, clientid):
        """create client release contract object for the specified clientid"""
        check_client_existence(clientid)

        data = request.get_json()
        data["clientid"] = clientid
        client_release_schema = ClientReleaseSchema()
        client_release_form = client_release_schema.load(data)

        db.session.add(client_release_form)
        db.session.commit()
        to_pdf(clientid, self.doctype)
        return client_release_form

@ns.route('/policies/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class PoliciesContract(Resource):
    """Client policies form"""

    doctype = DOCTYPE.policies
    docrev = DOCTYPE_DOCREV_MAP[doctype]

    @ns.doc(security='apikey')
    @token_auth.login_required
    @responds(schema=ClientPoliciesContractSchema, api=ns)
    def get(self, clientid):
        """returns most recent client policies table as a json for the clientid specified"""
        check_client_existence(clientid)

        client_policies =  ClientPolicies.query.filter_by(clientid=clientid).order_by(ClientPolicies.idx.desc()).first()

        if not client_services:
            raise ContentNotFound()
        return  client_policies

    @ns.doc(security='apikey')
    @accepts(schema=SignAndDateSchema, api=ns)
    @token_auth.login_required
    @responds(schema=ClientPoliciesContractSchema, status_code= 201, api=ns)
    def post(self, clientid):
        """create client policies contract object for the specified clientid"""
        check_client_existence(clientid)

        data = request.get_json()
        data["clientid"] = clientid
        client_policies_schema = ClientPoliciesContractSchema()
        client_policies = client_policies_schema.load(data)

        db.session.add(client_policies)
        db.session.commit()
        to_pdf(clientid, self.doctype)
        return client_policies

@ns.route('/consultcontract/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class ConsultConstract(Resource):
    """client consult contract"""

    doctype = DOCTYPE.consult
    docrev = DOCTYPE_DOCREV_MAP[doctype]

    @ns.doc(security='apikey')
    @token_auth.login_required
    @responds(schema=ClientConsultContractSchema, api=ns)
    def get(self, clientid):
        """returns most recent client consultation table as a json for the clientid specified"""
        check_client_existence(clientid)

        client_consult =  ClientConsultContract.query.filter_by(clientid=clientid).order_by(ClientConsultContract.idx.desc()).first()

        if not client_consult:
            raise ContentNotFound()
        return client_consult

    @accepts(schema=SignAndDateSchema, api=ns)
    @ns.doc(security='apikey')
    @token_auth.login_required
    @responds(schema=ClientConsultContractSchema, status_code= 201, api=ns)
    def post(self, clientid):
        """create client consult contract object for the specified clientid"""
        check_client_existence(clientid)

        data = request.get_json()
        data["clientid"] = clientid
        consult_contract_schema = ClientConsultContractSchema()
        client_consult = consult_contract_schema.load(data)
        
        db.session.add(client_consult)
        db.session.commit()
        to_pdf(clientid, self.doctype)
        return client_consult

@ns.route('/subscriptioncontract/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class SubscriptionContract(Resource):
    """client subscription contract"""

    doctype = DOCTYPE.subscription
    docrev = DOCTYPE_DOCREV_MAP[doctype]

    @ns.doc(security='apikey')
    @token_auth.login_required
    @responds(schema=ClientSubscriptionContractSchema, api=ns)
    def get(self, clientid):
        """returns most recent client subscription contract table as a json for the clientid specified"""
        check_client_existence(clientid)

        client_subscription =  ClientSubscriptionContract.query.filter_by(clientid=clientid).order_by(ClientSubscriptionContract.idx.desc()).first()
        if not client_subscription:
            raise ContentNotFound()
        return client_subscription

    @ns.doc(security='apikey')
    @accepts(schema=SignAndDateSchema, api=ns)
    @token_auth.login_required
    @responds(schema=ClientSubscriptionContractSchema, status_code= 201, api=ns)
    def post(self, clientid):
        """create client subscription contract object for the specified clientid"""
        check_client_existence(clientid)

        data = request.get_json()
        data["clientid"] = clientid
        subscription_contract_schema = ClientSubscriptionContractSchema()
        client_subscription = subscription_contract_schema.load(data)

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
        check_client_existence(clientid)
        
        client_services =  ClientIndividualContract.query.filter_by(clientid=clientid).order_by(ClientIndividualContract.idx.desc()).first()

        if not client_services:
            raise ContentNotFound()
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

    Returns a list of URLs to the stored the PDF documents.
    The URLs expire after 10 min.
    """
    @ns.doc(security='apikey')
    @token_auth.login_required
    @responds(schema=SignedDocumentsSchema, api=ns)
    def get(self, clientid):
        """Given a clientid, returns a list of URLs for all signed documents."""
        check_client_existence(clientid)

        urls = []

        if current_app.config['DOCS_STORE_LOCAL']:
            for table in (ClientPolicies,
                          ClientRelease,
                          ClientConsent,
                          ClientConsultContract,
                          ClientSubscriptionContract,
                          ClientIndividualContract):
                result = table.query.filter_by(clientid=clientid).order_by(table.idx.desc()).first()
                if result and result.pdf_path:
                    urls.append(result.pdf_path)
        else:
            s3 = boto3.client('s3')
            params = {
                'Bucket': current_app.config['DOCS_BUCKET_NAME'],
                'Key': None
            }

            for table in (ClientPolicies,
                          ClientRelease,
                          ClientConsent,
                          ClientConsultContract,
                          ClientSubscriptionContract,
                          ClientIndividualContract):
                result = table.query.filter_by(clientid=clientid).order_by(table.idx.desc()).first()
                if result and result.pdf_path:
                    params['Key'] = result.pdf_path
                    url = s3.generate_presigned_url('get_object', Params=params, ExpiresIn=600)
                    urls.append(url)

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
class RefreshRemoteRegistration(Resource):
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
        #prevent requests to set clientid and send message back to api user
        if data.get('clientid', None):
            raise IllegalSetting('clientid')

        client = ClientInfo.query.filter_by(email=token_auth_client.current_user().email).first()

        client.from_dict(data)
        db.session.add(client)
        db.session.commit()
        return client
