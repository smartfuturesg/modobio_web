import boto3
from datetime import datetime
import math, re

from flask import request, current_app
from flask_accepts import accepts, responds
from flask_restx import Resource
from sqlalchemy import select

from odyssey.api import api
from odyssey.utils.auth import token_auth, basic_auth
from odyssey.utils.errors import (
    UserNotFound, 
    ContentNotFound,
    IllegalSetting,
    TransactionNotFound, 
    InputError,
    GenericNotFound
)
from odyssey import db
from odyssey.utils.constants import TABLE_TO_URI
from odyssey.api.client.models import (
    ClientDataStorage,
    ClientInfo,
    ClientConsent,
    ClientConsultContract,
    ClientClinicalCareTeam,
    ClientClinicalCareTeamAuthorizations,
    ClientIndividualContract,
    ClientPolicies,
    ClientRelease,
    ClientSubscriptionContract,
    ClientFacilities,
    ClientMobileSettings,
    ClientAssignedDrinks,
    ClientHeightHistory,
    ClientWeightHistory,
    ClientWaistSizeHistory,
    ClientTransactionHistory,
    ClientPushNotifications
)
from odyssey.api.doctor.models import (
    MedicalFamilyHistory,
    MedicalGeneralInfo,
    MedicalGeneralInfoMedications,
    MedicalGeneralInfoMedicationAllergy,
    MedicalHistory, 
    MedicalPhysicalExam,               
    MedicalSocialHistory
)
from odyssey.api.lookup.models import (
    LookupClinicalCareTeamResources, 
    LookupDefaultHealthMetrics,
    LookupGoals, 
    LookupDrinks, 
    LookupRaces,
    LookupNotifications
)
from odyssey.api.physiotherapy.models import PTHistory 
from odyssey.api.staff.models import StaffRecentClients
from odyssey.api.trainer.models import FitnessQuestionnaire
from odyssey.api.facility.models import RegisteredFacilities
from odyssey.api.user.models import User, UserLogin, UserTokenHistory
from odyssey.utils.pdf import to_pdf, merge_pdfs
from odyssey.utils.email import send_test_email
from odyssey.utils.misc import check_client_existence, check_drink_existence
from odyssey.api.client.schemas import(
    AllClientsDataTier,
    ClientAssignedDrinksSchema,
    ClientAssignedDrinksDeleteSchema,
    ClientConsentSchema,
    ClientConsultContractSchema,
    ClientIndividualContractSchema,
    ClientClinicalCareTeamSchema,
    ClientMobileSettingsSchema,
    ClientMobilePushNotificationsSchema,
    ClientPoliciesContractSchema, 
    ClientRegistrationStatusSchema,
    ClientReleaseSchema,
    ClientReleaseContactsSchema,
    ClientSearchOutSchema,
    ClientSubscriptionContractSchema,
    ClientAndUserInfoSchema,
    ClientHeightSchema,
    ClientWeightSchema,
    ClientWaistSizeSchema,
    ClientTokenRequestSchema,
    ClinicalCareTeamAuthorizationNestedSchema,
    ClinicalCareTeamMemberOfSchema,
    SignAndDateSchema,
    SignedDocumentsSchema,
    ClientTransactionHistorySchema,
    ClientSearchItemsSchema
)
from odyssey.api.lookup.schemas import LookupDefaultHealthMetricsSchema
from odyssey.api.staff.schemas import StaffRecentClientsSchema
from odyssey.api.facility.schemas import ClientSummarySchema

ns = api.namespace('client', description='Operations related to clients')

@ns.route('/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class Client(Resource):
    @token_auth.login_required
    @responds(schema=ClientAndUserInfoSchema, api=ns)
    def get(self, user_id):
        """returns client info table as a json for the user_id specified"""

        client_data = ClientInfo.query.filter_by(user_id=user_id).one_or_none()
        user_data = User.query.filter_by(user_id=user_id).one_or_none()
        if not client_data and not user_data:
            raise UserNotFound(user_id)

        #update staff recent clients information
        staff_user_id = token_auth.current_user()[0].user_id

        #check if supplied client is already in staff recent clients
        client_exists = StaffRecentClients.query.filter_by(user_id=staff_user_id).filter_by(client_user_id=user_id).one_or_none()
        if client_exists:
            #update timestamp
            client_exists.timestamp = datetime.now()
            db.session.add(client_exists)
            db.session.commit()
        else:
            #enter new recent client information
            recent_client_schema = StaffRecentClientsSchema().load({'user_id': staff_user_id, 'client_user_id': user_id})
            db.session.add(recent_client_schema)
            db.session.flush()

            #check if staff member has more than 10 recent clients
            staff_recent_searches = StaffRecentClients.query.filter_by(user_id=staff_user_id).order_by(StaffRecentClients.timestamp.asc()).all()
            if len(staff_recent_searches) > 10:
                #remove the oldest client in the list
                db.session.delete(staff_recent_searches[0])
            db.session.commit()

        #data must be refreshed because of db changes
        if client_data:
            db.session.refresh(client_data)
        if user_data:
            db.session.refresh(user_data)
       
        client_info_payload = client_data.__dict__
        client_info_payload["primary_goal"] = db.session.query(LookupGoals.goal_name).filter(client_data.primary_goal_id == LookupGoals.goal_id).one_or_none()
        client_info_payload["race"] = db.session.query(LookupRaces.race_name).filter(client_data.race_id == LookupRaces.race_id).one_or_none()

        return {'client_info': client_info_payload, 'user_info': user_data}

    @token_auth.login_required
    @accepts(schema=ClientAndUserInfoSchema, api=ns)
    @responds(schema=ClientAndUserInfoSchema, status_code=200, api=ns)
    def put(self, user_id):
        """edit client info"""

        client_data = ClientInfo.query.filter_by(user_id=user_id).one_or_none()
        
        user_data = User.query.filter_by(user_id=user_id).one_or_none()

        if not client_data or not user_data:
            raise UserNotFound(user_id)
        
        #validate primary_goal_id if supplied and automatically create drink recommendation
        if 'primary_goal_id' in request.parsed_obj['client_info'].keys():
            goal = LookupGoals.query.filter_by(goal_id=request.parsed_obj['client_info']['primary_goal_id']).one_or_none()
            if not goal:
                raise InputError(400, 'Invalid primary_goal_id.')
            
            #make automatic drink recommendation
            drink_id = LookupDrinks.query.filter_by(primary_goal_id=request.parsed_obj['client_info']['primary_goal_id']).one_or_none().drink_id
            recommendation = ClientAssignedDrinksSchema().load({'drink_id': drink_id})
            recommendation.user_id = user_id
            db.session.add(recommendation)

        #update both tables with request data
        if request.parsed_obj['client_info']:
            client_data.update(request.parsed_obj['client_info'])
        if request.parsed_obj['user_info']:
            user_data.update(request.parsed_obj['user_info'])

        db.session.commit()

        # prepare client_info payload  
        client_info_payload = client_data.__dict__
        client_info_payload["primary_goal"] = db.session.query(LookupGoals.goal_name).filter(client_data.primary_goal_id == LookupGoals.goal_id).one_or_none()
        client_info_payload["race"] = db.session.query(LookupRaces.race_name).filter(client_data.race_id == LookupRaces.race_id).one_or_none()

        return {'client_info': client_data, 'user_info': user_data}

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

#Depricated 
@ns.route('/clientsearch/')
@ns.doc(params={'page': 'request page for paginated clients list',
                'per_page': 'number of clients per page',
                'firstname': 'first name to search',
                'lastname': 'last name to search',
                'email': 'email to search',
                'phone': 'phone number to search',
                'dob': 'date of birth to search',
                'record_locator_id': 'record locator id to search'})
class ClientsDepricated(Resource):
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

@ns.route('/search/')
class Clients(Resource):
    @ns.doc(params={'_from': 'starting at result 0, from what result to display',
                'per_page': 'number of clients per page',
                'firstname': 'first name to search',
                'lastname': 'last name to search',
                'email': 'email to search',
                'phone': 'phone number to search',
                'dob': 'date of birth to search',
                'modobio_id': 'modobio id to search'})
    @token_auth.login_required
    @responds(schema=ClientSearchOutSchema, api=ns)
    def get(self):
        """returns list of clients given query parameters,"""
        #if ELASTICSEARCH_URL isn't set, the search request will return without doing anything
        es = current_app.elasticsearch
        if not es: return
        
        #clean up and validate input data
        startAt = request.args.get('_from', 0, type= int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)

        if startAt < 0: raise InputError(400, '_from must be greater than or equal to 0')
        if per_page <= 0: raise InputError(400, 'per_page must be greater than 0')

        param = {}
        search = ''
        keys = request.args.keys()
        for key in keys:
            param[key] = request.args.get(key, default='')
            if key == 'phone' and param[key]:
                param[key] = re.sub("[^0-9]", "", param[key])      
            if key not in ['_from', 'per_page', 'dob'] and param[key]:
                search += param[key] + ' '

        #build ES query body
        if param.get('dob'):
            body={"query":{"bool":{"must":{"multi_match":{"query": search.strip(), "fuzziness":"AUTO:1,2", "zero_terms_query": "all"}},"filter":{"term":{"dob":param.get('dob')}}}},"from":startAt,"size":per_page}
        else:
            body={"query":{"multi_match":{"query": search.strip(), "fuzziness": "AUTO:1,2" ,"zero_terms_query": "all"}},"from":startAt,"size":per_page}
        #query ES index
        results=es.search(index="clients", body=body)

        #Format return data
        total_hits = results['hits']['total']['value']
        items = []
        for hit in results['hits']['hits']: items.append(ClientSearchItemsSchema().load(hit['_source']))
        
        response = {
            '_meta': {
                'from_result': startAt,
                'per_page': per_page,
                'total_pages': math.ceil(total_hits/per_page),
                'total_items': total_hits,
            }, 
            '_links': {
                '_self': api.url_for(Clients, _from=startAt, per_page=per_page),
                '_next': api.url_for(Clients, _from=startAt + per_page, per_page=per_page)
                if startAt + per_page < total_hits else None,
                '_prev': api.url_for(Clients, _from= startAt-per_page if startAt-per_page >=0 else 0, per_page=per_page)
                if startAt != 0 else None,
            }, 
            'items': items}
        
        #TODO maybe elasticsarch-DSL
        #This search works by searching the input fields and making a few changes in case of a typo, but
        #will only return exact matches for input strings of length one or two 
        return response

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
                MedicalGeneralInfo,
                MedicalGeneralInfoMedications,
                MedicalGeneralInfoMedicationAllergy,
                MedicalSocialHistory,
                MedicalFamilyHistory,
                MedicalPhysicalExam,
                PTHistory
        ):
            result = table.query.filter_by(user_id=user_id).order_by(table.idx.desc()).first()

            if result is None:
                remaining_forms.append({'name': table.displayname, 'URI': TABLE_TO_URI.get(table.__tablename__).format(user_id)})

        return {'outstanding': remaining_forms}

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
        query = db.session.execute(
            select(ClientDataStorage)
        ).scalars().all()

        total_bytes = sum(dat.total_bytes for dat in query)
        total_items = len(query)

        payload = {'total_stored_bytes': total_bytes, 'total_items': total_items, 'items': query}

        return payload

@ns.route('/token/')
class ClientToken(Resource):
    """create and revoke tokens"""
    @ns.doc(security='password')
    @basic_auth.login_required(user_type=('client',), email_required=False)
    @responds(schema=ClientTokenRequestSchema, status_code=201, api=ns)
    def post(self):
        """generates a token for the 'current_user' immediately after password authentication"""
        user, user_login = basic_auth.current_user()
        if not user:
            return 401
        
        access_token = UserLogin.generate_token(user_type='client', user_id=user.user_id, token_type='access')
        refresh_token = UserLogin.generate_token(user_type='client', user_id=user.user_id, token_type='refresh')

        db.session.add(UserTokenHistory(user_id=user.user_id, 
                                        refresh_token=refresh_token,
                                        event='login',
                                        ua_string = request.headers.get('User-Agent')))
        db.session.commit()

        return {'email': user.email, 
                'firstname': user.firstname, 
                'lastname': user.lastname, 
                'token': access_token,
                'refresh_token': refresh_token,
                'user_id': user.user_id,
                'email_verified': user.email_verified}

    @ns.doc(security='password')
    @token_auth.login_required(user_type=('client',))
    def delete(self):
        """
        Deprecated 11.19.20..does nothing now
        invalidate urrent token. Used to effectively logout a user
        """
        return '', 200


@ns.route('/clinical-care-team/members/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ClinicalCareTeamMembers(Resource):
    """
    Create update and remove members of a client's clinical care team
    only the client themselves may have access to these operations.
    """
    @token_auth.login_required(user_type=('client',))
    @accepts(schema=ClientClinicalCareTeamSchema, api=ns)
    @responds(schema=ClientClinicalCareTeamSchema, api=ns, status_code=201)
    def post(self, user_id):
        """
        Make a new entry into a client's clinical care team using only the new team 
        member's email. Clients may only have 6 team members stored. 

        Emails are checked against the database. If the email is associated with a current user, 
        the user's id is stored in the ClientClinicalCareTeam table. Otherwise, just the 
        email address is registered. 

        Parameters
        ----------
        user_id : int
            User ID number

        Expected payload includes
        email : str
            Email of new care team member
        Returns
        -------
        dict
            Returns the entries into the clinical care team. 
        """
        
        data = request.parsed_obj

        user = token_auth.current_user()[0]

        current_team = ClientClinicalCareTeam.query.filter_by(user_id=user_id).all()
        current_team_emails = [x.team_member_email for x in current_team]

        # prevent users from having more than 6 clinical care team members
        if len(current_team) + len(data.get("care_team")) > 6:
            raise InputError(message="Attemping to add too many team members", status_code=400)

        # enter new team members into client's clinical care team
        # if email is associated with a current user account, add that user's id to 
        #  the database entry
        for team_member in data.get("care_team"):
            if team_member["team_member_email"] == user.email:
                continue
            if team_member["team_member_email"].lower() in current_team_emails:
                continue

            team_memeber_user = User.query.filter_by(email=team_member["team_member_email"].lower()).one_or_none()
            if team_memeber_user:
                db.session.add(ClientClinicalCareTeam(**{"team_member_email": team_member["team_member_email"],
                                                         "team_member_user_id": team_memeber_user.user_id,
                                                         "user_id": user_id}))
            else:
                db.session.add(ClientClinicalCareTeam(**{"team_member_email": team_member["team_member_email"],
                                                       "user_id": user_id}))
            
        db.session.commit()

        # prepare response with names for clinical care team members who are also users 
        current_team = ClientClinicalCareTeam.query.filter_by(user_id=user_id, team_member_user_id=None).all() # non-users

        current_team_users = db.session.query(
                                    ClientClinicalCareTeam, User.firstname, User.lastname, User.modobio_id
                                ).filter(
                                    ClientClinicalCareTeam.user_id == user_id
                                ).filter(ClientClinicalCareTeam.team_member_user_id == User.user_id
                                ).all()
        
        for team_member in current_team_users:
            team_member[0].__dict__.update({'firstname': team_member[1], 'lastname': team_member[2], 'modobio_id': team_member[3]})
            current_team.append(team_member[0])
        
        response = {"care_team": current_team,
                    "total_items": len(current_team) }

        return response

    @token_auth.login_required(user_type=('client',))
    @accepts(schema=ClientClinicalCareTeamSchema, api=ns)
    def delete(self, user_id):
        """
        Remove members of a client's clinical care team using the team member's email address.
        Any matches between the incoming payload and current team members in the DB will be removed. 

        Parameters
        ----------
        user_id : int
            User ID number

        Expected payload includes
        email : str
            Email of new care team member
        Returns
        -------
        200 OK
        """
        
        data = request.parsed_obj
       
        for team_member in data.get("care_team"):
            ClientClinicalCareTeam.query.filter_by(user_id=user_id, team_member_email=team_member['team_member_email'].lower()).delete()
            
        db.session.commit()

        return 200

    @token_auth.login_required(user_type=('client',))
    @responds(schema=ClientClinicalCareTeamSchema, api=ns, status_code=200)
    def get(self, user_id):
        """
        Returns the client's clinical care team 

        Parameters
        ----------
        user_id : int
            User ID number

        Expected payload includes
        email : str
            Email of new care team member
        Returns
        -------
        200 OK
        """
        updates = False
        # check if any team members are users
        # if so, update their entry in the care team table with their user_id
        current_team_non_users = ClientClinicalCareTeam.query.filter_by(user_id=user_id, team_member_user_id=None).all()
        
        for team_member in current_team_non_users:
            team_memeber_user = User.query.filter_by(email=team_member.team_member_email).one_or_none()

            if team_memeber_user:
                team_member.team_member_user_id = team_memeber_user.user_id
                db.session.add(team_memeber_user)
                updates=True

        if updates:
            db.session.commit()
            current_team = ClientClinicalCareTeam.query.filter_by(user_id=user_id, team_member_user_id=None).all()
        else:
            current_team = current_team_non_users
        
        # prepare response with names for clinical care team members who are also users 
        current_team_users = db.session.query(
                                    ClientClinicalCareTeam, User.firstname, User.lastname, User.modobio_id
                                ).filter(
                                    ClientClinicalCareTeam.user_id == user_id
                                ).filter(ClientClinicalCareTeam.team_member_user_id == User.user_id
                                ).all()

        for team_member in current_team_users:
            team_member[0].__dict__.update({'firstname': team_member[1], 'lastname': team_member[2], 'modobio_id': team_member[3]})
            current_team.append(team_member[0])
        
        response = {"care_team": current_team,
                    "total_items": len(current_team) }

        return response

@ns.route('/clinical-care-team/member-of/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class UserClinicalCareTeamApi(Resource):
    """
    Clinical care teams the speficied user is part of
    
    Endpoint for viewing and managing the list of clients who have the specified user as part of their care team.
    """
    @token_auth.login_required
    @responds(schema=ClinicalCareTeamMemberOfSchema, api=ns, status_code=200)
    def get(self, user_id):
        """
        returns the list of clients whose clinical care team the given user_id
        is a part of
        """
        res = []
        for client in ClientClinicalCareTeam.query.filter_by(team_member_user_id=user_id).all():
            user = User.query.filter_by(user_id=client.user_id).one_or_none()
            authorizations_query = db.session.query(
                                    ClientClinicalCareTeamAuthorizations.resource_id, 
                                    LookupClinicalCareTeamResources.display_name
                                ).filter(
                                    ClientClinicalCareTeamAuthorizations.team_member_user_id == user_id
                                ).filter(
                                    ClientClinicalCareTeamAuthorizations.user_id == client.user_id
                                ).filter(
                                    ClientClinicalCareTeamAuthorizations.resource_id == LookupClinicalCareTeamResources.resource_id
                                ).all()
            res.append({'client_user_id': user.user_id, 
                        'client_name': ' '.join(filter(None, (user.firstname, user.middlename ,user.lastname))),
                        'client_email': user.email,
                        'client_modobio_id': user.modobio_id,
                        'authorizations': [{'display_name': x[1], 'resource_id': x[0]} for x in authorizations_query]})
        
        return {'member_of_care_teams': res, 'total': len(res)}

@ns.route('/clinical-care-team/resource-authorization/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ClinicalCareTeamResourceAuthorization(Resource):
    """
    Create, update, remove, retrieve authorization of resource access for care team members.

    Clinical care team members must individually be given access to resources. The available options can be found
    by using the /lookup/care-team/resources/ (GET) API. 
    """
    @token_auth.login_required(user_type=('client',))
    @accepts(schema=ClinicalCareTeamAuthorizationNestedSchema, api=ns)
    @responds(schema=ClinicalCareTeamAuthorizationNestedSchema, api=ns, status_code=201)
    def post(self, user_id):
        """
        Add new clinical care team authorizations for the specified user_id 
        """
        data = request.parsed_obj

        current_team_ids = db.session.query(ClientClinicalCareTeam.team_member_user_id).filter(ClientClinicalCareTeam.user_id==user_id).all()
        current_team_ids = [x[0] for x in current_team_ids if x[0] is not None]

        care_team_resources = LookupClinicalCareTeamResources.query.all()
        care_team_resources_ids = [x.resource_id for x in care_team_resources]

        for authorization in data.get('clinical_care_team_authoriztion'):
            if authorization.team_member_user_id in current_team_ids and authorization.resource_id in care_team_resources_ids:
                authorization.user_id = user_id
                db.session.add(authorization)
            else:
                raise InputError(message="team member not in care team or resource_id is invalid", status_code=400)
        try:
            db.session.commit()
        except Exception as e:
            raise InputError(message=e._message(), status_code=400)

        return 

    @token_auth.login_required(user_type=('client',))
    @responds(schema=ClinicalCareTeamAuthorizationNestedSchema, api=ns, status_code=200)
    def get(self, user_id):
        """
        Retrieve client's clinical care team authorizations
        """

        data = db.session.query(
            ClientClinicalCareTeamAuthorizations.resource_id, 
            LookupClinicalCareTeamResources.display_name,
            User.firstname, 
            User.lastname, 
            User.email,
            User.user_id,
            User.modobio_id
            ).filter(
                ClientClinicalCareTeamAuthorizations.user_id == user_id
            ).filter(
                User.user_id == ClientClinicalCareTeamAuthorizations.team_member_user_id
            ).filter(ClientClinicalCareTeamAuthorizations.resource_id == LookupClinicalCareTeamResources.resource_id
            ).all()
            
        care_team_auths =[]
        for row in data:
            tmp = {
                'resource_id': row[0],
                'display_name': row[1],
                'team_member_firstname': row[2],
                'team_member_lastname': row[3],
                'team_member_email': row[4],
                'team_member_user_id': row[5],
                'team_member_modobio_id': row[6]}

            care_team_auths.append(tmp)
        
        payload = {'clinical_care_team_authoriztion': care_team_auths}

        return payload

    @token_auth.login_required(user_type=('client',))
    @accepts(schema=ClinicalCareTeamAuthorizationNestedSchema, api=ns)

    def delete(self, user_id):
        """
        Remove a previously saved authorization. Takes the same payload as the POST method.
        """
        data = request.parsed_obj

        for dat in data.get('clinical_care_team_authoriztion'):
            authorization = ClientClinicalCareTeamAuthorizations.query.filter_by(
                                                                                resource_id = dat.resource_id,
                                                                                team_member_user_id = dat.team_member_user_id
                                                                                ).one_or_none()
            if authorization:
                db.session.delete(authorization)

        db.session.commit()

        return {}, 200


@ns.route('/drinks/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ClientDrinksApi(Resource):
    """
    Endpoints related to nutritional beverages that are assigned to clients.
    """
    @token_auth.login_required(user_type=('staff',), staff_role=('doctor', 'nutrition'))
    @accepts(schema=ClientAssignedDrinksSchema, api=ns)
    @responds(schema=ClientAssignedDrinksSchema, api=ns, status_code=201)
    def post(self, user_id):
        """
        Add an assigned drink to the client designated by user_id.
        """
        check_client_existence(user_id)
        check_drink_existence(request.parsed_obj.drink_id)

        request.parsed_obj.user_id = user_id
        db.session.add(request.parsed_obj)
        db.session.commit()

        return request.parsed_obj

    @token_auth.login_required
    @responds(schema=ClientAssignedDrinksSchema(many=True), api=ns, status_code=200)
    def get(self, user_id):
        """
        Returns the list of drinks assigned to the user designated by user_id.
        """
        check_client_existence(user_id)

        return ClientAssignedDrinks.query.filter_by(user_id=user_id).all()
    
    @token_auth.login_required(user_type=('staff',), staff_role=('doctor', 'nutrition'))
    @accepts(schema=ClientAssignedDrinksDeleteSchema, api=ns)
    @responds(schema=ClientAssignedDrinksSchema, api=ns, status_code=204)
    def delete(self, user_id):
        """
        Delete a drink assignemnt for a user with user_id and drink_id
        """
        for drink_id in request.parsed_obj['drink_ids']:
            drink = ClientAssignedDrinks.query.filter_by(user_id=user_id, drink_id=drink_id).one_or_none()

            if not drink:
                raise ContentNotFound()

            db.session.delete(drink)
        
        db.session.commit()

@ns.route('/mobile-settings/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ClientMobileSettingsApi(Resource):
    """
    For the client to change their own mobile settings
    """
    @token_auth.login_required(user_type=('client',))
    @accepts(schema=ClientMobileSettingsSchema, api=ns)
    @responds(schema=ClientMobileSettingsSchema, api=ns, status_code=201)
    def post(self, user_id):
        """
        Set a client's mobile settings for the first time
        """

        check_client_existence(user_id)

        if ClientMobileSettings.query.filter_by(user_id=user_id).one_or_none():
            raise IllegalSetting(message=f"Mobile settings for user_id {user_id} already exists. Please use PUT method")

        gen_settings = request.parsed_obj['general_settings']
        gen_settings.user_id = user_id
        db.session.add(gen_settings)

        for notification in request.parsed_obj['push_notification_type_ids']:
            exists = LookupNotifications.query.filter_by(notification_type_id=notification.notification_type_id).one_or_none()
            if not exists:
                raise GenericNotFound(message="Invalid notification type id: " + str(notification.notification_type_id))
           
            push_notfication = ClientMobilePushNotificationsSchema().load({'notification_type_id': notification.notification_type_id})
            push_notfication.user_id = user_id
            db.session.add(push_notfication)

        db.session.commit()

        return request.json

    @token_auth.login_required(user_type=('client',))
    @responds(schema=ClientMobileSettingsSchema, api=ns, status_code=200)
    def get(self, user_id):
        """
        Returns the mobile settings that a client has set.
        """

        check_client_existence(user_id)

        gen_settings = ClientMobileSettings.query.filter_by(user_id=user_id).one_or_none()

        notification_types = ClientPushNotifications.query.filter_by(user_id=user_id).all()

        return {'general_settings': gen_settings, 'push_notification_type_ids': notification_types}

    @token_auth.login_required(user_type=('client',))
    @accepts(schema=ClientMobileSettingsSchema, api=ns)
    @responds(schema=ClientMobileSettingsSchema, api=ns, status_code=200)
    def put(self, user_id):
        """
        Update a client's mobile settings
        """

        check_client_existence(user_id)
        settings = ClientMobileSettings.query.filter_by(user_id=user_id).one_or_none()
        if not settings:
            raise IllegalSetting(message=f"Mobile settings for user_id {user_id} do not exist. Please use POST method")

        gen_settings = request.parsed_obj['general_settings'].__dict__
        del gen_settings['_sa_instance_state']
        settings.update(gen_settings)

        client_push_notifications = ClientPushNotifications.query.filter_by(user_id=user_id).all()
        client_new_notifications = []
        for notification in request.parsed_obj['push_notification_type_ids']:
            exists = LookupNotifications.query.filter_by(notification_type_id=notification.notification_type_id).one_or_none()
            if not exists:
                raise GenericNotFound(message="Invalid notification type id: " + str(notification.notification_type_id))
            
            client_new_notifications.append(notification.notification_type_id)
            
        for notification in client_push_notifications:
            if notification.notification_type_id not in client_new_notifications:
                #if an id type is not in the arguments, the user has disabled this type of notification
                db.session.delete(notification)
            else:
                #if a notification type with this id is already in the db, remove from the list
                #of new types to be added for the user
                client_new_notifications.remove(notification.notification_type_id)

        for notification_type_id in client_new_notifications:
            push_notification = ClientMobilePushNotificationsSchema().load({'notification_type_id': notification_type_id})
            push_notification.user_id = user_id
            db.session.add(push_notification)

        db.session.commit()
        return request.json

@ns.route('/height/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ClientHeightApi(Resource):
    """
    Endpoints related to submitting client height and viewing
    a client's height history.
    """
    @token_auth.login_required(user_type=('client',))
    @accepts(schema=ClientHeightSchema, api=ns)
    @responds(schema=ClientHeightSchema, api=ns, status_code=201)
    def post(self, user_id):
        """
        Submits a new height for the client.
        """
        check_client_existence(user_id)

        request.parsed_obj.user_id = user_id
        db.session.add(request.parsed_obj)

        #clientInfo should hold the most recent height given for the client so update here
        client = ClientInfo.query.filter_by(user_id=user_id)
        client.update({'height': request.parsed_obj.height})

        db.session.commit()
        return request.parsed_obj

    @token_auth.login_required(user_type=('client', 'staff'))
    @responds(schema=ClientHeightSchema(many=True), api=ns, status_code=200)
    def get(self, user_id):
        """
        Returns all heights reported for a client and the dates they were reported.
        """
        check_client_existence(user_id)

        return ClientHeightHistory.query.filter_by(user_id=user_id).all()

@ns.route('/weight/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ClientWeightApi(Resource):
    """
    Endpoints related to submitting client weight and viewing
    a client's weight history.
    """
    @token_auth.login_required(user_type=('client',))
    @accepts(schema=ClientWeightSchema, api=ns)
    @responds(schema=ClientWeightSchema, api=ns, status_code=201)
    def post(self, user_id):
        """
        Submits a new weight for the client.
        """
        check_client_existence(user_id)

        request.parsed_obj.user_id = user_id
        db.session.add(request.parsed_obj)

        #clientInfo should hold the most recent height given for the client so update here
        client = ClientInfo.query.filter_by(user_id=user_id)
        client.update({'weight': request.parsed_obj.weight})

        db.session.commit()
        return request.parsed_obj

    @token_auth.login_required(user_type=('client', 'staff'))
    @responds(schema=ClientWeightSchema(many=True), api=ns, status_code=200)
    def get(self, user_id):
        """
        Returns all weights reported for a client and the dates they were reported.
        """
        check_client_existence(user_id)

        return ClientWeightHistory.query.filter_by(user_id=user_id).all()

@ns.route('/waist-size/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ClientWaistSizeApi(Resource):
    """
    Endpoints related to submitting client waist size and viewing
    a client's waist size history.
    """
    @token_auth.login_required(user_type=('client',))
    @accepts(schema=ClientWaistSizeSchema, api=ns)
    @responds(schema=ClientWaistSizeSchema, api=ns, status_code=201)
    def post(self, user_id):
        """
        Submits a new waist size for the client.
        """
        check_client_existence(user_id)

        request.parsed_obj.user_id = user_id
        db.session.add(request.parsed_obj)

        #clientInfo should hold the most recent waist size given for the client so update here
        client = ClientInfo.query.filter_by(user_id=user_id)
        client.update({'waist_size': request.parsed_obj.waist_size})

        db.session.commit()
        return request.parsed_obj

    @token_auth.login_required(user_type=('client', 'staff'))
    @responds(schema=ClientWaistSizeSchema(many=True), api=ns, status_code=200)
    def get(self, user_id):
        """
        Returns all waist sizes reported for a client and the dates they were reported.
        """
        check_client_existence(user_id)

        return ClientWaistSizeHistory.query.filter_by(user_id=user_id).all()

@ns.route('/transaction/history/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ClientTransactionHistoryApi(Resource):
    """
    Endpoints related to viewing a client's transaction history.
    """
    @token_auth.login_required(user_type=('client','staff'), staff_role=('client_services',))
    @responds(schema=ClientTransactionHistorySchema(many=True), api=ns, status_code=200)
    def get(self, user_id):
        """
        Returns a list of all transactions for the given user_id.
        """
        check_client_existence(user_id)

        return ClientTransactionHistory.query.filter_by(user_id=user_id).all()

@ns.route('/transaction/<int:transaction_id>/')
@ns.doc(params={'transaction_id': 'Transaction ID number'})
class ClientTransactionApi(Resource):
    """
    Viewing and editing transactions
    """

    @token_auth.login_required(user_type=('client','staff'), staff_role=('client_services',))
    @responds(schema=ClientTransactionHistorySchema, api=ns, status_code=200)
    def get(self, transaction_id):
        """
        Returns information about the transaction identified by transaction_id.
        """
        transaction = ClientTransactionHistory.query.filter_by(idx=transaction_id).one_or_none()
        if not transaction:
            raise TransactionNotFound(transaction_id)

        return transaction


    @token_auth.login_required(user_type=('client','staff'), staff_role=('client_services',))
    @accepts(schema=ClientTransactionHistorySchema, api=ns)
    @responds(schema=ClientTransactionHistorySchema, api=ns, status_code=201)
    def put(self, transaction_id):
        """
        Updates the transaction identified by transaction_id.
        """
        transaction = ClientTransactionHistory.query.filter_by(idx=transaction_id).one_or_none()
        if not transaction:
            raise TransactionNotFound(transaction_id)

        data = request.json

        transaction.update(data)
        db.session.commit()

        return request.parsed_obj


@ns.route('/transaction/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ClientTransactionPutApi(Resource):
    """
    Viewing and editing transactions
    """
    @token_auth.login_required(user_type=('client','staff'), staff_role=('client_services',))
    @accepts(schema=ClientTransactionHistorySchema, api=ns)
    @responds(schema=ClientTransactionHistorySchema, api=ns, status_code=201)
    def post(self, user_id):
        """
        Submits a transaction for the client identified by user_id.
        """
        check_client_existence(user_id)

        request.parsed_obj.user_id = user_id
        db.session.add(request.parsed_obj)
        db.session.commit()

        return request.parsed_obj

@ns.route('/default-health-metrics/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ClientWeightApi(Resource):
    """
    Endpoint for returning the recommended health metrics for the client based on age and sex
    """
    @token_auth.login_required()
    @responds(schema=LookupDefaultHealthMetricsSchema, api=ns, status_code=200)
    def get(self, user_id):
        """
        Looks up client's age and sex. One or both are not available, we return our best guess: the health
        metrics for a 30 year old female.
        """
        client_info = ClientInfo.query.filter_by(user_id=user_id).one_or_none()
        user_info, _ = token_auth.current_user()
        
        # get user sex and age info
        if user_info.biological_sex_male != None:
            sex = ('m' if user_info.biological_sex_male else 'f')
        elif client_info.gender in ('m', 'f'): # use gender instead of biological sex
            sex = client_info.gender
        else: # default to female
            sex = 'f'
        
        if client_info.dob:
            years_old = round((datetime.now().date()-client_info.dob).days/365.25)
        else: # default to 30 years old if not dob is present
            years_old = 30

        age_categories = db.session.query(LookupDefaultHealthMetrics.age).filter(LookupDefaultHealthMetrics.sex == 'm').all()
        age_categories = [x[0] for x in age_categories]
        age_category = min(age_categories, key=lambda x:abs(x-years_old))

        health_metrics = LookupDefaultHealthMetrics.query.filter_by(age = age_category).filter_by(sex = sex).one_or_none()
        
        return health_metrics
