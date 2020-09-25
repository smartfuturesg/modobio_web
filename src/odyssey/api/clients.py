import boto3
from datetime import datetime, date

from flask import request, jsonify, current_app
from flask_accepts import accepts, responds
from flask_restx import Resource, Api

from odyssey.api import api
from odyssey.api.auth import token_auth, token_auth_client
from odyssey.api.errors import UserNotFound, ClientAlreadyExists, ClientNotFound, IllegalSetting, ContentNotFound
from odyssey import db
from odyssey.constants import TABLE_TO_URI
from odyssey.models.client import (
    ClientInfo,
    ClientConsent,
    ClientConsultContract,
    ClientIndividualContract,
    ClientPolicies,
    ClientRelease,
    ClientSubscriptionContract,
    ClientFacilities,
    RemoteRegistration
)
from odyssey.models.doctor import MedicalHistory, MedicalPhysicalExam
from odyssey.models.pt import PTHistory 
from odyssey.models.staff import ClientRemovalRequests
from odyssey.models.trainer import FitnessQuestionnaire
from odyssey.models.misc import RegisteredFacilities
from odyssey.pdf import to_pdf, merge_pdfs
from odyssey.utils.email import send_email_remote_registration_portal, send_test_email
from odyssey.utils.misc import check_client_existence
from odyssey.utils.schemas import (
    ClientSearchSchema,
    ClientConsentSchema,
    ClientConsultContractSchema,
    ClientIndividualContractSchema,
    ClientInfoSchema,
    ClientPoliciesContractSchema, 
    ClientRegistrationStatusSchema,
    ClientReleaseSchema,
    ClientReleaseContactsSchema,
    ClientRemoteRegistrationPortalSchema, 
    ClientSubscriptionContractSchema,
    NewRemoteClientSchema, 
    RefreshRemoteRegistrationSchema,
    SignAndDateSchema,
    SignedDocumentsSchema
)

ns = api.namespace('client', description='Operations related to clients')

@ns.route('/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class Client(Resource):
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
        elif data.get('membersince', None):
            raise IllegalSetting('membersince')
        
        client.update(data)
        db.session.commit()
        
        return client

@ns.route('/remove/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class RemoveClient(Resource):
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
        #set member since date to today
        data['membersince'] = date.today().strftime("%Y-%m-%d")
        
        client = ClientInfoSchema().load(data)
        db.session.add(client)
        db.session.flush()

        rli = {'record_locator_id': ClientInfo().get_medical_record_hash(firstname = client.firstname , lastname = client.lastname, clientid =client.clientid)}

        client.update(rli)
        db.session.commit()

        return client

@ns.route('/sidebar/<int:clientid>/')
class ClientSidebar(Resource):
    @token_auth.login_required
    def get(self, clientid):
        client = ClientInfo.query.get(clientid)
        if not client:
            raise UserNotFound(clientid)
        
        #get list of a client's registered facilities' addresses
        clientFacilities = ClientFacilities.query.filter_by(client_id=clientid).all()
        facilityList = [item.facility_id for item in clientFacilities]
        facilities = []
        for item in facilityList:
            facilities.append(RegisteredFacilities.query.filter_by(facility_id=item).first().facility_address)

        #ensure dates are not null
        membersince, dob = None, None
        if not client.membersince == None:
            membersince = client.membersince.strftime("%Y-%m-%d")
        if not client.dob == None:
            dob = client.dob.strftime("%Y-%m-%d")

        response = {"firstname": client.firstname, "middlename": client.middlename, "lastname": client.lastname,
                    "dob": dob, "clientid": client.clientid, "membersince": membersince, "facilities": facilities}
        return response

@ns.route('/clientsearch/')
@ns.doc(params={'page': 'request page for paginated clients list', 'per_page': 'number of clients per page'})
class Clients(Resource):
    @token_auth.login_required
    @accepts(schema=ClientSearchSchema, api=ns)
    def get(self):
        """returns list of all clients"""
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)                 
        
        payload = request.get_json()
        # These payload keys should be the same as what's indexed in 
        # the model.
        payload_keys = ['firstname', 'lastname', 'email', 'phone', 'dob', 'record_locator_id']
        
        searchStr = ''
 
        if not payload:
            data, resources = ClientInfo.all_clients_dict(ClientInfo.query.order_by(ClientInfo.lastname.asc()),
                                                page=page,per_page=per_page)
        else:
            # DOB is a string that needs to be broken up without the "-"
            # for whooshee search
            if payload.get('dob', None):
                payload['dob'] = payload['dob'].replace("-"," ")
            # Go through the payload, and enter an empty string for missing keys
            for key in payload_keys:
                if key not in payload:
                    payload[key]=''
                searchStr = searchStr + payload[key] + ' '
            data, resources = ClientInfo.all_clients_dict(ClientInfo.query.whooshee_search(searchStr).order_by(ClientInfo.lastname.asc()),
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
    @token_auth.login_required
    @responds(schema=ClientConsentSchema, status_code=201, api=ns)
    def post(self, clientid):
        """ Create client consent contract for the specified clientid """
        check_client_existence(clientid)

        data = request.get_json()
        data["clientid"] = clientid

        client_consent_schema = ClientConsentSchema()
        client_consent_form = client_consent_schema.load(data)
        client_consent_form.revision = ClientConsent.current_revision
        
        db.session.add(client_consent_form)
        db.session.commit()

        to_pdf(clientid, ClientConsent)
        return client_consent_form

@ns.route('/release/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class ReleaseContract(Resource):
    """Client release forms"""

    @token_auth.login_required
    @responds(schema=ClientReleaseSchema, api=ns)
    def get(self, clientid):
        """returns most recent client release table as a json for the clientid specified"""
        check_client_existence(clientid)

        client_release_contract =  ClientRelease.query.filter_by(clientid=clientid).order_by(ClientRelease.idx.desc()).first()

        if not client_release_contract:
            raise ContentNotFound()

        return client_release_contract

    @accepts(schema=ClientReleaseSchema)
    @token_auth.login_required
    @responds(schema=ClientReleaseSchema, status_code=201, api=ns)
    def post(self, clientid):
        """create client release contract object for the specified clientid"""
        check_client_existence(clientid)

        data = request.get_json()
        
        # add client id to release contract 
        data["clientid"] = clientid

        # load the client release contract into the db and flush
        client_release_contract = ClientReleaseSchema().load(data)
        client_release_contract.revision = ClientRelease.current_revision

        # add release contract to session and flush to get index (foreign key to the release contacts)
        db.session.add(client_release_contract)
        db.session.flush()
        
        release_to_data = data["release_to"]
        release_from_data = data["release_from"]

        # add clientid to each release contact
        release_contacts = []
        for item in release_to_data + release_from_data:
            item["clientid"] = clientid
            item["release_contract_id"] = client_release_contract.idx
            release_contacts.append(item)
        
        # load contacts and rest of release form into objects seperately
        release_contact_objects = ClientReleaseContactsSchema(many=True).load(release_contacts)

        db.session.add_all(release_contact_objects)

        db.session.commit()
        to_pdf(clientid, ClientRelease)
        return client_release_contract

@ns.route('/policies/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class PoliciesContract(Resource):
    """Client policies form"""

    @token_auth.login_required
    @responds(schema=ClientPoliciesContractSchema, api=ns)
    def get(self, clientid):
        """returns most recent client policies table as a json for the clientid specified"""
        check_client_existence(clientid)

        client_policies =  ClientPolicies.query.filter_by(clientid=clientid).order_by(ClientPolicies.idx.desc()).first()

        if not client_policies:
            raise ContentNotFound()
        return  client_policies

    @accepts(schema=ClientPoliciesContractSchema, api=ns)
    @token_auth.login_required
    @responds(schema=ClientPoliciesContractSchema, status_code= 201, api=ns)
    def post(self, clientid):
        """create client policies contract object for the specified clientid"""
        check_client_existence(clientid)

        data = request.get_json()
        data["clientid"] = clientid
        client_policies_schema = ClientPoliciesContractSchema()
        client_policies = client_policies_schema.load(data)
        client_policies.revision = ClientPolicies.current_revision

        db.session.add(client_policies)
        db.session.commit()
        to_pdf(clientid, ClientPolicies)
        return client_policies

@ns.route('/consultcontract/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class ConsultConstract(Resource):
    """client consult contract"""

    @token_auth.login_required
    @responds(schema=ClientConsultContractSchema, api=ns)
    def get(self, clientid):
        """returns most recent client consultation table as a json for the clientid specified"""
        check_client_existence(clientid)

        client_consult =  ClientConsultContract.query.filter_by(clientid=clientid).order_by(ClientConsultContract.idx.desc()).first()

        if not client_consult:
            raise ContentNotFound()
        return client_consult

    @accepts(schema=ClientConsultContractSchema, api=ns)
    @token_auth.login_required
    @responds(schema=ClientConsultContractSchema, status_code= 201, api=ns)
    def post(self, clientid):
        """create client consult contract object for the specified clientid"""
        check_client_existence(clientid)

        data = request.get_json()
        data["clientid"] = clientid
        consult_contract_schema = ClientConsultContractSchema()
        client_consult = consult_contract_schema.load(data)
        client_consult.revision = ClientConsultContract.current_revision
        
        db.session.add(client_consult)
        db.session.commit()
        to_pdf(clientid, ClientConsultContract)
        return client_consult

@ns.route('/subscriptioncontract/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class SubscriptionContract(Resource):
    """client subscription contract"""

    @token_auth.login_required
    @responds(schema=ClientSubscriptionContractSchema, api=ns)
    def get(self, clientid):
        """returns most recent client subscription contract table as a json for the clientid specified"""
        check_client_existence(clientid)

        client_subscription =  ClientSubscriptionContract.query.filter_by(clientid=clientid).order_by(ClientSubscriptionContract.idx.desc()).first()
        if not client_subscription:
            raise ContentNotFound()
        return client_subscription

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
        client_subscription.revision = ClientSubscriptionContract.current_revision

        db.session.add(client_subscription)
        db.session.commit()
        to_pdf(clientid, ClientSubscriptionContract)
        return client_subscription

@ns.route('/servicescontract/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class IndividualContract(Resource):
    """client individual services contract"""

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
    @responds(schema=ClientIndividualContractSchema,status_code=201, api=ns)
    def post(self, clientid):
        """create client individual services contract object for the specified clientid"""
        data = request.get_json()
        data['clientid'] = clientid
        data['revision'] = ClientIndividualContract.current_revision

        client_services = ClientIndividualContract(**data)

        db.session.add(client_services)
        db.session.commit()
        to_pdf(clientid, ClientIndividualContract)
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
    @token_auth.login_required
    @responds(schema=SignedDocumentsSchema, api=ns)
    def get(self, clientid):
        """ Given a clientid, returns a dict of URLs for all signed documents.

        Parameters
        ----------
        clientid : int
            Client ID number

        Returns
        -------
        dict
            Keys are the display names of the documents,
            values are URLs to the generated PDF documents.
        """
        check_client_existence(clientid)

        urls = {}
        paths = []

        bucket_name = current_app.config['DOCS_BUCKET_NAME']
        if not bucket_name:
            raise IllegalSetting(message='Bucket name not defined.')

        if not current_app.config['LOCAL_CONFIG']:
            s3 = boto3.client('s3')
            params = {
                'Bucket': bucket_name,
                'Key': None
            }

        for table in (
            ClientPolicies,
            ClientConsent,
            ClientRelease,
            ClientConsultContract,
            ClientSubscriptionContract,
            ClientIndividualContract
        ):
            result = (
                table.query
                .filter_by(clientid=clientid)
                .order_by(table.idx.desc())
                .first()
            )
            if result and result.pdf_path:
                paths.append(result.pdf_path)
                if not current_app.config['LOCAL_CONFIG']:
                    params['Key'] = result.pdf_path
                    url = s3.generate_presigned_url('get_object', Params=params, ExpiresIn=600)
                    urls[table.displayname] = url
                else:
                    urls[table.displayname] = result.pdf_path

        concat = merge_pdfs(paths, clientid)
        urls['All documents'] = concat

        return {'urls': urls}

@ns.route('/registrationstatus/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class JourneyStatusCheck(Resource):
    """
        Returns the outstanding forms needed to complete the client journey
    """
    @responds(schema=ClientRegistrationStatusSchema, api=ns)
    @token_auth.login_required
    def get(self, clientid):
        """
        Returns the client's outstanding registration items and their URIs.
        """
        check_client_existence(clientid)

        remaining_forms = []

        for table in (
                ClientPolicies,
                ClientConsent,
                ClientRelease,
                ClientConsultContract,
                ClientSubscriptionContract,
                ClientIndividualContract,
                FitnessQuestionnaire,
                MedicalHistory,
                MedicalPhysicalExam,
                PTHistory
        ):
            result = table.query.filter_by(clientid=clientid).order_by(table.idx.desc()).first()

            if result is None:
                remaining_forms.append({'name': table.displayname, 'URI': TABLE_TO_URI.get(table.__tablename__).format(clientid)})

        return {'outstanding': remaining_forms}



@ns.route('/remoteregistration/new/')
class NewRemoteRegistration(Resource):
    """
        initialize a client for remote registration
    """
    @token_auth.login_required
    @accepts(schema=NewRemoteClientSchema, api=ns)
    @responds(schema=ClientRemoteRegistrationPortalSchema, api=ns, status_code=201)
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
        rr_schema = NewRemoteClientSchema() #creates entry into clientinfo table
        client_rr_schema = ClientRemoteRegistrationPortalSchema() #remote registration table entry

        # enter client into basic info table and remote register table
        client = rr_schema.load(data)
        
        # add client to database (creates clientid)
        db.session.add(client)
        db.session.flush()

        rli = {'record_locator_id': ClientInfo().get_medical_record_hash(firstname = client.firstname , lastname = client.lastname, clientid =client.clientid)}

        client.update(rli)        
        db.session.flush()

        # create a new remote client registration entry
        portal_data = {'clientid' : client.clientid, 'email': client.email}
        remote_client_portal = client_rr_schema.load(portal_data)

        db.session.add(remote_client_portal)
        db.session.commit()

        if not current_app.config['LOCAL_CONFIG']:
            # send email to client containing registration details
            send_email_remote_registration_portal(
                recipient=remote_client_portal.email, 
                password=remote_client_portal.password, 
                remote_registration_portal=remote_client_portal.registration_portal_id
            )

        return remote_client_portal


@ns.route('/remoteregistration/refresh/')
class RefreshRemoteRegistration(Resource):
    """
        refresh client portal a client for remote registration
    """
    @token_auth.login_required
    @accepts(schema=RefreshRemoteRegistrationSchema)
    @responds(schema=ClientRemoteRegistrationPortalSchema, api=ns, status_code=201)
    def post(self):
        """refresh the portal endpoint and password
        """
        data = request.get_json() #should only need the email

        client = ClientInfo.query.filter_by(email=data.get('email', None)).first()

        #if client isnt in the database return error
        if not client:
            raise ClientNotFound(identification = data['email'])

        client_rr_schema = ClientRemoteRegistrationPortalSchema() #remote registration table entry
        #add clientid to the data object from the current client
        data['clientid'] =  client.clientid

        # create a new remote client session registration entry
        remote_client_portal = client_rr_schema.load(data)

        # create temporary password and portal url

        db.session.add(remote_client_portal)
        db.session.commit()

        if not current_app.config['LOCAL_CONFIG']:
            # send email to client containing registration details
            send_email_remote_registration_portal(
                recipient=remote_client_portal.email,
                password=remote_client_portal.password, 
                remote_registration_portal=remote_client_portal.registration_portal_id
            )

        return remote_client_portal


@ns.route('/testemail/')
class TestEmail(Resource):
    """
       Send a test email
    """
    @token_auth.login_required
    @ns.doc(params={'recipient': 'test email recipient'})
    def get(self):
        """send a testing email"""
        recipient = request.args.get('recipient')

        send_test_email(recipient=recipient)
        
        return {}, 200  