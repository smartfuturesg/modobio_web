import boto3
from datetime import date, datetime, timedelta
import jwt

from flask import request, current_app
from flask_accepts import accepts, responds
from flask_restx import Resource, Api

from odyssey.api import api
from odyssey.utils.auth import token_auth, basic_auth
from odyssey.utils.errors import (
    UserNotFound, 
    ClientAlreadyExists, 
    ClientNotFound,
    ContentNotFound,
    IllegalSetting, 
    InputError
)
from odyssey import db
from odyssey.utils.constants import TABLE_TO_URI
from odyssey.api.client.models import (
    ClientInfo,
    ClientConsent,
    ClientConsultContract,
    ClientClinicalCareTeam,
    ClientIndividualContract,
    ClientPolicies,
    ClientRelease,
    ClientSubscriptionContract,
    ClientFacilities,
    ClientAssignedDrinks
)
from odyssey.api.doctor.models import MedicalHistory, MedicalPhysicalExam
from odyssey.api.physiotherapy.models import PTHistory 
from odyssey.api.staff.models import StaffRecentClients
from odyssey.api.trainer.models import FitnessQuestionnaire
from odyssey.api.facility.models import RegisteredFacilities
from odyssey.api.user.models import User, UserLogin
from odyssey.utils.pdf import to_pdf, merge_pdfs
from odyssey.utils.email import send_email_user_registration_portal, send_test_email
from odyssey.utils.misc import check_client_existence, check_drink_existence
from odyssey.api.client.schemas import(
    AllClientsDataTier,
    ClientAssignedDrinksSchema,
    ClientAssignedDrinksDeleteSchema,
    ClientConsentSchema,
    ClientConsultContractSchema,
    ClientIndividualContractSchema,
    ClientInfoSchema,
    ClientClinicalCareTeamSchema,
    ClientPoliciesContractSchema, 
    ClientRegistrationStatusSchema,
    ClientReleaseSchema,
    ClientReleaseContactsSchema,
    ClientSearchOutSchema,
    ClientSubscriptionContractSchema,
    ClientAndUserInfoSchema,
    NewRemoteClientSchema,
    SignAndDateSchema,
    SignedDocumentsSchema
)
from odyssey.api.staff.schemas import StaffRecentClientsSchema
from odyssey.api.facility.schemas import ClientSummarySchema
from odyssey.api.user.schemas import UserSchema

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
        return {'client_info': client_data, 'user_info': user_data}

    @token_auth.login_required
    @accepts(schema=ClientAndUserInfoSchema, api=ns)
    @responds(schema=ClientAndUserInfoSchema, status_code=200, api=ns)
    def put(self, user_id):
        """edit client info"""

        client_data = ClientInfo.query.filter_by(user_id=user_id).one_or_none()
        user_data = User.query.filter_by(user_id=user_id).one_or_none()

        if not client_data or not user_data:
            raise UserNotFound(user_id)
        
        #update both tables with request data
        if request.parsed_obj['client_info']:
            client_data.update(request.parsed_obj['client_info'])
        if request.parsed_obj['user_info']:
            user_data.update(request.parsed_obj['user_info'])

        db.session.commit()
        
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
    
@ns.route('/token/')
class ClientToken(Resource):
    """create and revoke tokens"""
    @ns.doc(security='password')
    @basic_auth.login_required(user_type=('client',))
    def post(self):
        """generates a token for the 'current_user' immediately after password authentication"""
        user, _ = basic_auth.current_user()
        if not user:
            return 401
        
        access_token = UserLogin.generate_token(user_type='client', user_id=user.user_id, token_type='access')
        refresh_token = UserLogin.generate_token(user_type='client', user_id=user.user_id, token_type='refresh')

        return {'email': user.email, 
                'firstname': user.firstname, 
                'lastname': user.lastname, 
                'token': access_token,
                'refresh_token': refresh_token,
                'user_id': user.user_id}, 201

    @ns.doc(security='password')
    @token_auth.login_required(user_type=('client',))
    def delete(self):
        """
        Deprecated 11.19.20..does nothing now
        invalidate urrent token. Used to effectively logout a user
        """
        return '', 200


@ns.route('/clinical-care-team/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ClinicalCareTeam(Resource):
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
                                    ClientClinicalCareTeam, User.firstname, User.lastname
                                ).filter(
                                    ClientClinicalCareTeam.team_member_user_id == User.user_id
                                ).all()
        
        for team_member in current_team_users:
            team_member[0].__dict__.update({'firstname': team_member[1], 'lastname': team_member[2]})
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
                                    ClientClinicalCareTeam, User.firstname, User.lastname
                                ).filter(
                                    ClientClinicalCareTeam.team_member_user_id == User.user_id
                                ).all()
        
        for team_member in current_team_users:
            team_member[0].__dict__.update({'firstname': team_member[1], 'lastname': team_member[2]})
            current_team.append(team_member[0])
        
        response = {"care_team": current_team,
                    "total_items": len(current_team) }

        return response

@ns.route('/drinks/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ClientDrinksApi(Resource):
    """
    Endpoints related to nutritional beverages that are assigned to clients.
    """
    @token_auth.login_required(user_type=('staff',), staff_role=('doctor', 'nutrition', 'doctor_internal', 'nutrition_internal'))
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
    
    @token_auth.login_required(user_type=('staff',), staff_role=('doctor', 'nutrition', 'doctor_internal', 'nutrition_internal'))
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