import boto3
from datetime import date

from flask import request, current_app
from flask_accepts import accepts, responds
from flask_restx import Resource, Api

from odyssey.api import api
from odyssey.utils.auth import token_auth, basic_auth
from odyssey.utils.errors import (
    UserNotFound, 
    ClientAlreadyExists, 
    ClientNotFound,
    IllegalSetting, 
    ContentNotFound
)
from odyssey import db
from odyssey.utils.constants import TABLE_TO_URI
from odyssey.api.client.models import (
    ClientInfo,
    ClientConsent,
    ClientConsultContract,
    ClientIndividualContract,
    ClientPolicies,
    ClientRelease,
    ClientSubscriptionContract,
    ClientFacilities
)
from odyssey.api.doctor.models import MedicalHistory, MedicalPhysicalExam
from odyssey.api.physiotherapy.models import PTHistory 
from odyssey.api.staff.models import ClientRemovalRequests
from odyssey.api.trainer.models import FitnessQuestionnaire
from odyssey.api.facility.models import RegisteredFacilities
from odyssey.api.user.models import User
from odyssey.utils.pdf import to_pdf, merge_pdfs
from odyssey.utils.email import send_email_remote_registration_portal, send_test_email
from odyssey.utils.misc import check_client_existence
from odyssey.api.client.schemas import(
    AllClientsDataTier,
    ClientConsentSchema,
    ClientConsultContractSchema,
    ClientIndividualContractSchema,
    ClientInfoSchema,
    ClientPoliciesContractSchema, 
    ClientRegistrationStatusSchema,
    ClientReleaseSchema,
    ClientReleaseContactsSchema,
    ClientSearchOutSchema,
    ClientSubscriptionContractSchema,
    NewRemoteClientSchema,
    SignAndDateSchema,
    SignedDocumentsSchema
)
from odyssey.api.facility.schemas import ClientSummarySchema
from odyssey.api.user.schemas import UserSchema

ns = api.namespace('client', description='Operations related to clients')

@ns.route('/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class Client(Resource):
    @token_auth.login_required
    @responds(schema=ClientInfoSchema, api=ns)
    def get(self, user_id):
        """returns client info table as a json for the user_id specified"""
        client_data = db.session.query(
                    ClientInfo, User
                ).filter(
                    ClientInfo.user_id == user_id
                ).filter(
                    User.user_id == user_id
                ).first()
        if not client_data:
            raise UserNotFound(user_id)
        return client_data

    @token_auth.login_required
    @accepts(schema=ClientInfoSchema, api=ns)
    @responds(status_code=200, api=ns)
    def put(self, user_id):
        """edit client info"""
        data = request.get_json()

        client_info_data = ClientInfo.query.filter_by(user_id=user_id).one_or_none()

        if not client_info_data:
            raise UserNotFound(user_id)
        #prevent requests to set user_id and send message back to api user
        elif data.get('user_id', None):
            raise IllegalSetting('user_id')
        elif data.get('membersince', None):
            raise IllegalSetting('membersince')

        client_info_data.update(data)
        db.session.commit()
        
        return 


#############
#temporarily disabled until a better user delete system is created
#############

# @ns.route('/remove/<int:user_id>/')
# @ns.doc(params={'user_id': 'User ID number'})
# class RemoveClient(Resource):
#     @token_auth.login_required
#     def delete(self, user_id):
#         """deletes client from database entirely"""
#         client = User.query.filter_by(user_id=user_id, is_client=True).one_or_none()

#         if not client:
#             raise ClientNotFound(user_id)
        
#         if client.is_staff:
#             #only delete the client portio

#         # find the staff member requesting client delete
#         staff = token_auth.current_user()
#         new_removal_request = ClientRemovalRequests(user_id=staff.user_id)
        
#         db.session.add(new_removal_request)
#         db.session.flush()

#         #TODO: some logic on who gets to delete clients+ email to staff admin
#         db.session.delete(client)
#         db.session.commit()
        
#         return {'message': f'client with id {user_id} has been removed'}

@ns.route('/summary/<int:user_id>/')
class ClientSummary(Resource):
    @token_auth.login_required
    @responds(schema=ClientSummarySchema, api=ns)
    def get(self, user_id):
        user = User.query.filter_by(user_id=user_id).one_or_none()
        client = ClientInfo.query.filter_by(user_id=user_id).one_or_none()
        if not client:
            raise UserNotFound(user_id)
        
        #get list of a client's registered facilities' addresses
        clientFacilities = ClientFacilities.query.filter_by(user_id=user_id).all()
        facilityList = [item.facility_id for item in clientFacilities]
        facilities = []
        for item in facilityList:
            facilities.append(RegisteredFacilities.query.filter_by(facility_id=item).first())
            
        data = {"firstname": user.firstname, "middlename": user.middlename, "lastname": user.lastname,
                "user_id": user.user_id, "dob": client.dob, "membersince": client.membersince, "facilities": facilities}
        return data

@ns.route('/clientsearch/')
@ns.doc(params={'page': 'request page for paginated clients list',
                'per_page': 'number of clients per page',
                'firstname': 'first name to search',
                'lastname': 'last name to search',
                'email': 'email to search',
                'phone': 'phone number to search',
                'dob': 'date of birth to search',
                'record_locator_id': 'record locator id to search'})

#todo - fix to work with new user system
class Clients(Resource):
    @token_auth.login_required
    @responds(schema=ClientSearchOutSchema, api=ns)
    #@responds(schema=UserSchema(many=True), api=ns)
    def get(self):
        """returns list of clients given query parameters"""
        clients = []
        for user in User.query.filter_by(is_client=True).all():
            client = {
                'user_id': user.user_id,
                'firstname': user.firstname,
                'lastname': user.lastname,
                'email': user.email,
                'phone': user.phone_number,
                'dob': None,
                'record_locator_id': None,
                'modobio_id': user.modobio_id
            }
            clients.append(client)
        response = {'items': clients, '_meta': None, '_links': None}
        return response

        # page = request.args.get('page', 1, type=int)
        # per_page = min(request.args.get('per_page', 10, type=int), 100)                 
        
        # # These payload keys should be the same as what's indexed in 
        # # the model.
        # param = {}
        # param_keys = ['firstname', 'lastname', 'email', 'phone', 'dob', 'record_locator_id']
        # searchStr = ''
        # for key in param_keys:
        #     param[key] = request.args.get(key, default=None, type=str)
        #     # Cleans up search query
        #     if param[key] is None:
        #         param[key] = ''          
        #     elif key == 'record_locator_id' and param.get(key, None):
        #         tempId = param[key]
        #     elif key == 'email' and param.get(key, None):
        #         tempEmail = param[key]
        #         param[key] = param[key].replace("@"," ")
        #     elif key == 'phone' and param.get(key, None):
        #         param[key] = param[key].replace("-"," ")
        #         param[key] = param[key].replace("("," ")
        #         param[key] = param[key].replace(")"," ")                
        #     elif key == 'dob' and param.get(key, None):
        #         param[key] = param[key].replace("-"," ")

        #     searchStr = searchStr + param[key] + ' '        
        
        # if(searchStr.isspace()):
        #     data, resources = ClientInfo.all_clients_dict(ClientInfo.query.order_by(ClientInfo.lastname.asc()),
        #                                         page=page,per_page=per_page)
        # else:
        #     data, resources = ClientInfo.all_clients_dict(ClientInfo.query.whooshee_search(searchStr),
        #                                         page=page,per_page=per_page)

        # # Since email and record locator idshould be unique, 
        # # if the input email or rli exactly matches 
        # # the profile, only display that user
        # exactMatch = False
        
        # if param['email']:
        #     for val in data['items']:
        #         if val['email'].lower() == tempEmail.lower():
        #             data['items'] = [val]
        #             exactMatch = True
        #             break
        
        # # Assuming client will most likely remember their 
        # # email instead of their RLI. If the email is correct
        # # no need to search through RLI. 
        # #
        # # If BOTH are incorrect, return data as normal.
        # if param['record_locator_id'] and not exactMatch:
        #     for val in data['items']:
        #         if val['record_locator_id'] is None:
        #             pass
        #         elif val['record_locator_id'].lower() == tempId.lower():
        #             data['items'] = [val]
        #             break

        # data['_links']= {
        #     '_self': api.url_for(Clients, page=page, per_page=per_page),
        #     '_next': api.url_for(Clients, page=page + 1, per_page=per_page)
        #     if resources.has_next else None,
        #     '_prev': api.url_for(Clients, page=page - 1, per_page=per_page)
        #     if resources.has_prev else None,
        # }
        
        # return data

@ns.route('/consent/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ConsentContract(Resource):
    """client consent forms"""

    @token_auth.login_required
    @responds(schema=ClientConsentSchema, api=ns)
    def get(self, user_id):
        """returns the most recent consent table as a json for the user_id specified"""
        check_client_existence(user_id)

        client_consent_form = ClientConsent.query.filter_by(user_id=user_id).order_by(ClientConsent.idx.desc()).first()
        
        if not client_consent_form:
            raise ContentNotFound()

        return client_consent_form

    @accepts(schema=ClientConsentSchema, api=ns)
    @token_auth.login_required
    @responds(schema=ClientConsentSchema, status_code=201, api=ns)
    def post(self, user_id):
        """ Create client consent contract for the specified user_id """
        check_client_existence(user_id)

        data = request.get_json()
        data["user_id"] = user_id

        client_consent_schema = ClientConsentSchema()
        client_consent_form = client_consent_schema.load(data)
        client_consent_form.revision = ClientConsent.current_revision
        
        db.session.add(client_consent_form)
        db.session.commit()

        to_pdf(user_id, ClientConsent)
        return client_consent_form

@ns.route('/release/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ReleaseContract(Resource):
    """Client release forms"""

    @token_auth.login_required
    @responds(schema=ClientReleaseSchema, api=ns)
    def get(self, user_id):
        """returns most recent client release table as a json for the user_id specified"""
        check_client_existence(user_id)

        client_release_contract =  ClientRelease.query.filter_by(user_id=user_id).order_by(ClientRelease.idx.desc()).first()

        if not client_release_contract:
            raise ContentNotFound()

        return client_release_contract

    @accepts(schema=ClientReleaseSchema)
    @token_auth.login_required
    @responds(schema=ClientReleaseSchema, status_code=201, api=ns)
    def post(self, user_id):
        """create client release contract object for the specified user_id"""
        check_client_existence(user_id)

        data = request.get_json()
        
        # add client id to release contract 
        data["user_id"] = user_id

        # load the client release contract into the db and flush
        client_release_contract = ClientReleaseSchema().load(data)
        client_release_contract.revision = ClientRelease.current_revision

        # add release contract to session and flush to get index (foreign key to the release contacts)
        db.session.add(client_release_contract)
        db.session.flush()
        
        release_to_data = data["release_to"]
        release_from_data = data["release_from"]

        # add user_id to each release contact
        release_contacts = []
        for item in release_to_data + release_from_data:
            item["user_id"] = user_id
            item["release_contract_id"] = client_release_contract.idx
            release_contacts.append(item)
        
        # load contacts and rest of release form into objects seperately
        release_contact_objects = ClientReleaseContactsSchema(many=True).load(release_contacts)

        db.session.add_all(release_contact_objects)

        db.session.commit()
        to_pdf(user_id, ClientRelease)
        return client_release_contract

@ns.route('/policies/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class PoliciesContract(Resource):
    """Client policies form"""

    @token_auth.login_required
    @responds(schema=ClientPoliciesContractSchema, api=ns)
    def get(self, user_id):
        """returns most recent client policies table as a json for the user_id specified"""
        check_client_existence(user_id)

        client_policies =  ClientPolicies.query.filter_by(user_id=user_id).order_by(ClientPolicies.idx.desc()).first()

        if not client_policies:
            raise ContentNotFound()
        return  client_policies

    @accepts(schema=ClientPoliciesContractSchema, api=ns)
    @token_auth.login_required
    @responds(schema=ClientPoliciesContractSchema, status_code= 201, api=ns)
    def post(self, user_id):
        """create client policies contract object for the specified user_id"""
        check_client_existence(user_id)

        data = request.get_json()
        data["user_id"] = user_id
        client_policies_schema = ClientPoliciesContractSchema()
        client_policies = client_policies_schema.load(data)
        client_policies.revision = ClientPolicies.current_revision

        db.session.add(client_policies)
        db.session.commit()
        to_pdf(user_id, ClientPolicies)
        return client_policies

@ns.route('/consultcontract/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ConsultConstract(Resource):
    """client consult contract"""

    @token_auth.login_required
    @responds(schema=ClientConsultContractSchema, api=ns)
    def get(self, user_id):
        """returns most recent client consultation table as a json for the user_id specified"""
        check_client_existence(user_id)

        client_consult =  ClientConsultContract.query.filter_by(user_id=user_id).order_by(ClientConsultContract.idx.desc()).first()

        if not client_consult:
            raise ContentNotFound()
        return client_consult

    @accepts(schema=ClientConsultContractSchema, api=ns)
    @token_auth.login_required
    @responds(schema=ClientConsultContractSchema, status_code= 201, api=ns)
    def post(self, user_id):
        """create client consult contract object for the specified user_id"""
        check_client_existence(user_id)

        data = request.get_json()
        data["user_id"] = user_id
        consult_contract_schema = ClientConsultContractSchema()
        client_consult = consult_contract_schema.load(data)
        client_consult.revision = ClientConsultContract.current_revision
        
        db.session.add(client_consult)
        db.session.commit()
        to_pdf(user_id, ClientConsultContract)
        return client_consult

@ns.route('/subscriptioncontract/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class SubscriptionContract(Resource):
    """client subscription contract"""

    @token_auth.login_required
    @responds(schema=ClientSubscriptionContractSchema, api=ns)
    def get(self, user_id):
        """returns most recent client subscription contract table as a json for the user_id specified"""
        check_client_existence(user_id)

        client_subscription =  ClientSubscriptionContract.query.filter_by(user_id=user_id).order_by(ClientSubscriptionContract.idx.desc()).first()
        if not client_subscription:
            raise ContentNotFound()
        return client_subscription

    @accepts(schema=SignAndDateSchema, api=ns)
    @token_auth.login_required
    @responds(schema=ClientSubscriptionContractSchema, status_code= 201, api=ns)
    def post(self, user_id):
        """create client subscription contract object for the specified user_id"""
        check_client_existence(user_id)

        data = request.get_json()
        data["user_id"] = user_id
        subscription_contract_schema = ClientSubscriptionContractSchema()
        client_subscription = subscription_contract_schema.load(data)
        client_subscription.revision = ClientSubscriptionContract.current_revision

        db.session.add(client_subscription)
        db.session.commit()
        to_pdf(user_id, ClientSubscriptionContract)
        return client_subscription

@ns.route('/servicescontract/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class IndividualContract(Resource):
    """client individual services contract"""

    @token_auth.login_required
    @responds(schema=ClientIndividualContractSchema, api=ns)
    def get(self, user_id):
        """returns most recent client individual servies table as a json for the user_id specified"""
        check_client_existence(user_id)
        
        client_services =  ClientIndividualContract.query.filter_by(user_id=user_id).order_by(ClientIndividualContract.idx.desc()).first()

        if not client_services:
            raise ContentNotFound()
        return  client_services

    @token_auth.login_required
    @accepts(schema=ClientIndividualContractSchema, api=ns)
    @responds(schema=ClientIndividualContractSchema,status_code=201, api=ns)
    def post(self, user_id):
        """create client individual services contract object for the specified user_id"""
        data = request.get_json()
        data['user_id'] = user_id
        data['revision'] = ClientIndividualContract.current_revision

        client_services = ClientIndividualContract(**data)

        db.session.add(client_services)
        db.session.commit()
        to_pdf(user_id, ClientIndividualContract)
        return client_services

@ns.route('/signeddocuments/<int:user_id>/', methods=('GET',))
@ns.doc(params={'user_id': 'User ID number'})
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
    def get(self, user_id):
        """ Given a user_id, returns a dict of URLs for all signed documents.

        Parameters
        ----------
        user_id : int
            User ID number

        Returns
        -------
        dict
            Keys are the display names of the documents,
            values are URLs to the generated PDF documents.
        """
        check_client_existence(user_id)

        urls = {}
        paths = []

        if not current_app.config['LOCAL_CONFIG']:
            s3 = boto3.client('s3')
            params = {
                'Bucket': current_app.config['S3_BUCKET_NAME'],
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
                .filter_by(user_id=user_id)
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

        concat = merge_pdfs(paths, user_id)
        urls['All documents'] = concat

        return {'urls': urls}

@ns.route('/registrationstatus/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class JourneyStatusCheck(Resource):
    """
        Returns the outstanding forms needed to complete the client journey
    """
    @responds(schema=ClientRegistrationStatusSchema, api=ns)
    @token_auth.login_required
    def get(self, user_id):
        """
        Returns the client's outstanding registration items and their URIs.
        """
        check_client_existence(user_id)

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
            result = table.query.filter_by(user_id=user_id).order_by(table.idx.desc()).first()

            if result is None:
                remaining_forms.append({'name': table.displayname, 'URI': TABLE_TO_URI.get(table.__tablename__).format(user_id)})

        return {'outstanding': remaining_forms}



# @ns.route('/remoteregistration/new/')
# class NewRemoteRegistration(Resource):
#     """
#         initialize a client for remote registration
#     """
#     @token_auth.login_required
#     @accepts(schema=NewRemoteClientSchema, api=ns)
#     @responds(schema=ClientRemoteRegistrationPortalSchema, api=ns, status_code=201)
#     def post(self):
#         """create new remote registration client
#             this will create a new entry into the client info table first
#             then create an entry into the Remote registration table
#             response includes the hash required to access the temporary portal for
#             this client
#         """
#         data = request.get_json()

#         #make sure this user email does not exist
#         if ClientInfo.query.filter_by(email=data.get('email', None)).first():
#             raise ClientAlreadyExists(identification = data['email'])

#         # initialize schema objects
#         rr_schema = NewRemoteClientSchema() #creates entry into clientinfo table
#         client_rr_schema = ClientRemoteRegistrationPortalSchema() #remote registration table entry

#         # enter client into basic info table and remote register table
#         client = rr_schema.load(data)
        
#         # add client to database (creates clientid)
#         db.session.add(client)
#         db.session.flush()

#         rli = {'record_locator_id': ClientInfo().generate_record_locator_id(firstname = client.firstname , lastname = client.lastname, clientid =client.clientid)}

#         client.update(rli)        
#         db.session.flush()

#         # create a new remote client registration entry
#         portal_data = {'clientid' : client.clientid, 'email': client.email}
#         remote_client_portal = client_rr_schema.load(portal_data)

#         db.session.add(remote_client_portal)
#         db.session.commit()

#         if not current_app.config['LOCAL_CONFIG']:
#             # send email to client containing registration details
#             send_email_remote_registration_portal(
#                 recipient=remote_client_portal.email, 
#                 password=remote_client_portal.password, 
#                 remote_registration_portal=remote_client_portal.registration_portal_id
#             )

#         return remote_client_portal


# @ns.route('/remoteregistration/refresh/')
# class RefreshRemoteRegistration(Resource):
#     """
#         refresh client portal a client for remote registration
#     """
#     @token_auth.login_required
#     @accepts(schema=RefreshRemoteRegistrationSchema, api=ns)
#     @responds(schema=ClientRemoteRegistrationPortalSchema, api=ns, status_code=201)
#     def post(self):
#         """refresh the portal endpoint and password
#         """
#         data = request.get_json() #should only need the email

#         client = ClientInfo.query.filter_by(email=data.get('email', None)).first()

#         #if client isnt in the database return error
#         if not client:
#             raise ClientNotFound(identification = data['email'])

#         client_rr_schema = ClientRemoteRegistrationPortalSchema() #remote registration table entry
#         #add clientid to the data object from the current client
#         data['clientid'] =  client.clientid

#         # create a new remote client session registration entry
#         remote_client_portal = client_rr_schema.load(data)

#         # create temporary password and portal url

#         db.session.add(remote_client_portal)
#         db.session.commit()

#         if not current_app.config['LOCAL_CONFIG']:
#             # send email to client containing registration details
#             send_email_remote_registration_portal(
#                 recipient=remote_client_portal.email,
#                 password=remote_client_portal.password, 
#                 remote_registration_portal=remote_client_portal.registration_portal_id
#             )

#         return remote_client_portal


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

@ns.route('/datastoragetiers/')
class ClientDataStorageTiers(Resource):
    """
       Amount of data stored on each client and their storage tier
    """
    @token_auth.login_required
    @responds(schema=AllClientsDataTier, api=ns)
    def get(self):
        """Returns the total data storage for each client along with their data storage tier"""

        data = db.session.execute("SELECT * FROM public.data_per_client;").fetchall()
        results = {'total_items': len(data), 'items' : []}
        total_bytes = 0
        for row in data:
            bytes_as_int = row[1].__int__()
            results['items'].append({'user_id': row[0], 'stored_bytes': bytes_as_int, 'tier': row[2]})
            total_bytes += bytes_as_int

        results['total_stored_bytes'] = total_bytes 
        
        return results

""" Client Token Endpoints """
@ns.route('/token/')
class ClientToken(Resource):
    """create and revoke tokens"""
    @ns.doc(security='password')
    @basic_auth.login_required(user_type=['client'])
    def post(self):
        """generates a token for the 'current_user' immediately after password authentication"""
        user, user_login = basic_auth.current_user()
        if not user:
            return 401
        return {'email': user.email, 
                'firstname': user.firstname, 
                'lastname': user.lastname, 
                'token': user_login.get_token()}, 201

    @ns.doc(security='password')
    @token_auth.login_required(user_type=['client'])
    def delete(self):
        """invalidate current token. Used to effectively logout a user"""
        token_auth.current_user()[1].revoke_token()
        return '', 204