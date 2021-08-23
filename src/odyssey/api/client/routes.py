from logging import error
import boto3
from datetime import datetime, timedelta
import math, re
from PIL import Image

from flask import request, current_app, url_for
from flask_accepts import accepts, responds
from flask_restx import Resource, Namespace
from sqlalchemy import select

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
from odyssey.utils.constants import TABLE_TO_URI, ALLOWED_IMAGE_TYPES, IMAGE_MAX_SIZE, IMAGE_DIMENSIONS
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
    ClientPushNotifications,
    ClientRaceAndEthnicity
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
    LookupCountriesOfOperations,
    LookupDefaultHealthMetrics,
    LookupGoals, 
    LookupDrinks,
    LookupMacroGoals, 
    LookupRaces,
    LookupNotifications,
    LookupTerritoriesOfOperations
)
from odyssey.api.physiotherapy.models import PTHistory 
from odyssey.api.staff.models import StaffProfile, StaffRecentClients, StaffRoles
from odyssey.api.telehealth.models import TelehealthBookings
from odyssey.api.trainer.models import FitnessQuestionnaire
from odyssey.api.facility.models import RegisteredFacilities
from odyssey.api.user.models import User, UserLogin, UserTokenHistory, UserProfilePictures
from odyssey.utils.pdf import to_pdf, merge_pdfs
from odyssey.utils.message import send_test_email
from odyssey.utils.misc import (
    check_client_existence, 
    check_drink_existence, 
    FileHandling
)

from odyssey.api.client.schemas import(
    AllClientsDataTier,
    ClientAssignedDrinksSchema,
    ClientAssignedDrinksDeleteSchema,
    ClientClinicalCareTeamDeleteSchema,
    ClientConsentSchema,
    ClientConsultContractSchema,
    ClientIndividualContractSchema,
    ClientClinicalCareTeamSchema,
    ClinicalCareTeamTemporaryMembersSchema,
    ClientMobileSettingsSchema,
    ClientMobilePushNotificationsSchema,
    ClientPoliciesContractSchema, 
    ClientRegistrationStatusSchema,
    ClientReleaseSchema,
    ClientReleaseContactsSchema,
    ClientSearchOutSchema,
    ClientSubscriptionContractSchema,
    ClientAndUserInfoSchema,
    ClientAndUserInfoPutSchema,
    ClientHeightSchema,
    ClientWeightSchema,
    ClientWaistSizeSchema,
    ClientTokenRequestSchema,
    ClinicalCareTeamAuthorizationNestedSchema,
    ClinicalCareTeamMemberOfSchema,
    SignAndDateSchema,
    SignedDocumentsSchema,
    ClientTransactionHistorySchema,
    ClientSearchItemsSchema,
    ClientRaceAndEthnicitySchema,
    ClientRaceAndEthnicityEditSchema,
    ClientInfoSchema
)
from odyssey.api.lookup.schemas import LookupDefaultHealthMetricsSchema
from odyssey.api.staff.schemas import StaffRecentClientsSchema
from odyssey.api.facility.schemas import ClientSummarySchema
from odyssey.utils.base.resources import BaseResource

ns = Namespace('client', description='Operations related to clients')

def process_race_and_ethnicity(user_id, mother, father):
    def format_list(ids):
        """
        removes duplicate ids if present,
        checks race_id 1 is exclusive if present
        checks that all ids are valid
        """

        #removes duplicate ids if they were submitted
        formatted_list = list(set(ids))

        #race_id 1 (unknown) must be exclusive, a user cannot submit 'unknown' and
        #other race(s) for a single parent
        if 1 in formatted_list and len(formatted_list) > 1:
            raise InputError(400, 'Race_id 1 (unknown) must be exclusive. It cannot be submitted in a list with other race ids.')

        for race_id in formatted_list:
            if not LookupRaces.query.filter_by(race_id=race_id).one_or_none():
                raise InputError(400, f'Invalid race_id: {race_id}')

        return formatted_list

    #remove existing race/ethnicity info
    for data in ClientRaceAndEthnicity.query.filter_by(user_id=user_id).all():
        db.session.delete(data)
    db.session.commit()

    #add incoming data from request
    if not mother:
        #if a blank array is passed, mark as 'unknown'
        model = ClientRaceAndEthnicitySchema().load({'is_client_mother': True, 'race_id': 1})
        model.user_id = user_id
        db.session.add(model)
    else:
        formatted_list = format_list(mother)
        for race_id in formatted_list:
            model = ClientRaceAndEthnicitySchema().load({
                'race_id': race_id,
                'is_client_mother': True
            })
            model.user_id = user_id
            db.session.add(model)

    if not father:
        #if a blank array is passed, mark as 'unknown'
        model = ClientRaceAndEthnicitySchema().load({'is_client_mother': False, 'race_id': 1})
        model.user_id = user_id
        db.session.add(model)
    else:
        formatted_list = format_list(father)
        for race_id in formatted_list:
            model = ClientRaceAndEthnicitySchema().load({
                'race_id': race_id,
                'is_client_mother': False
            })
            model.user_id = user_id
            db.session.add(model)

    db.session.commit()


@ns.route('/profile-picture/<int:user_id>/')
class ClientProfilePicture(BaseResource):
    """
    Enpoint to edit client's profile picture
    """
    @token_auth.login_required(user_type=('client',))
    @responds(schema=ClientInfoSchema(only=['user_id','profile_picture']), status_code=200, api=ns)
    def put(self, user_id):
        """
        Put will be used to add new or change a profile picture for a client

        Accepts form-data, will only handle one image
        "profile_picture": file (allowed types are '.png', '.jpg', '.jpeg')
        """
        super().check_user(user_id, user_type='client')

        if not ('profile_picture' in request.files and request.files['profile_picture']):  
            raise InputError(422, "No file selected")    

        # add all files to S3 - Naming it specifically as client_profile_picture to differentiate from staff profile pic
        # format: id{user_id:05d}/client_profile_picture/size{img.length}x{img.width}.img_extension
        fh = FileHandling()
        img = request.files['profile_picture']
        res = ClientInfo.query.filter_by(user_id=user_id).first().profile_pictures
        _prefix = f'id{user_id:05d}/client_profile_picture'

        # validate file size - safe threashold (MAX = 10 mb)
        fh.validate_file_size(img, IMAGE_MAX_SIZE)
        # validate file type
        img_extension = fh.validate_file_type(img, ALLOWED_IMAGE_TYPES)

        # if any, delete files with clien_profile_picture prefix
        fh.delete_from_s3(prefix=_prefix)
        # delete entries to UserProfilePictures in db
        for _obj in res:
            db.session.delete(_obj)

        # Save original to S3
        open_img = Image.open(img)
        img_w, img_h = open_img.size
        original_s3key = f'{_prefix}/original{img_extension}'
        fh.save_file_to_s3(img, original_s3key)

        # Save original to db
        user_profile_pic = UserProfilePictures()
        user_profile_pic.original = True
        user_profile_pic.client_id = user_id
        user_profile_pic.image_path = original_s3key
        user_profile_pic.width = img_w
        user_profile_pic.height = img_h
        db.session.add(user_profile_pic)

        # crop new uploaded image into a square
        squared = fh.image_crop_square(img)

        # resize to sizes specified by the tuple of tuples in constant IMAGE_DEMENSIONS
        for dimension in IMAGE_DIMENSIONS:
            _img = fh.image_resize(squared, dimension)
            # save to s3 bucket
            _img_s3key = f'{_prefix}/{_img.filename}'
            fh.save_file_to_s3(_img, _img_s3key)

            # save to database
            w, h = dimension
            user_profile_pic = UserProfilePictures()
            user_profile_pic.client_id = user_id
            user_profile_pic.image_path = _img_s3key
            user_profile_pic.width = w
            user_profile_pic.height = h
            db.session.add(user_profile_pic)

        # get presigned urls
        res = fh.get_presigned_urls(prefix=_prefix)
        img.close()

        db.session.commit()
        return {'user_id': user_id, 'profile_picture': res}

    @token_auth.login_required(user_type=('client',))
    @responds(status_code=204, api=ns)
    def delete(self, user_id):
        """
        Request to delete the client's profile picture
        """
        super().check_user(user_id, user_type='client')

        fh = FileHandling()
        _prefix = f'id{user_id:05d}/client_profile_picture'

        # if any, delete files with clien_profile_picture prefix
        fh.delete_from_s3(prefix=_prefix)

        # delete entries to UserProfilePictures in db
        res = ClientInfo.query.filter_by(user_id=user_id).first().profile_pictures
        for _obj in res:
            db.session.delete(_obj)

        db.session.commit()


@ns.route('/<int:user_id>/')
class Client(BaseResource):
    @token_auth.login_required
    @responds(schema=ClientAndUserInfoSchema, api=ns)
    def get(self, user_id):
        """returns client info table as a json for the user_id specified"""
        super().check_user(user_id, user_type='client')

        client_data = ClientInfo.query.filter_by(user_id=user_id).one_or_none()
        user_data = User.query.filter_by(user_id=user_id).one_or_none()
        if not client_data and not user_data:
            raise UserNotFound(user_id)

        #update staff recent clients information
        staff_user_id = token_auth.current_user()[0].user_id

        #if this request was made by a staff member, update their recent clients list
        if staff_user_id != user_id:
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
        client_info_payload["primary_macro_goal"] = db.session.query(LookupMacroGoals.goal).filter(client_data.primary_macro_goal_id == LookupMacroGoals.goal_id).one_or_none()
        client_info_payload["race_information"] = db.session.query(ClientRaceAndEthnicity.is_client_mother, LookupRaces.race_id, LookupRaces.race_name) \
            .join(LookupRaces, LookupRaces.race_id == ClientRaceAndEthnicity.race_id) \
            .filter(ClientRaceAndEthnicity.user_id == user_id).all()
        territory = LookupTerritoriesOfOperations.query.filter_by(idx=client_data.territory_id).one_or_none()
        if territory:
            client_info_payload["country"] = LookupCountriesOfOperations.query.filter_by(idx=territory.country_id).one_or_none().country
            client_info_payload["territory"] = territory.sub_territory
            client_info_payload["territory_abbreviation"] = territory.sub_territory_abbreviation

        #Include profile picture in different sizes
        if client_data.profile_pictures:
            fh = FileHandling()
            _prefix = f'id{user_id:05d}/client_profile_picture'
            client_info_payload["profile_picture"] = fh.get_presigned_urls(_prefix)

        return {'client_info': client_info_payload, 'user_info': user_data}

    @token_auth.login_required
    @accepts(schema=ClientAndUserInfoPutSchema, api=ns)
    @responds(schema=ClientAndUserInfoSchema, status_code=200, api=ns)
    def put(self, user_id):
        """edit client info"""

        super().check_user(user_id, user_type='client')

        client_data = ClientInfo.query.filter_by(user_id=user_id).one_or_none()
        
        user_data = User.query.filter_by(user_id=user_id).one_or_none()

        if not client_data or not user_data:
            raise UserNotFound(user_id)
        
        #validate primary_macro_goal_id
        if 'primary_macro_goal_id' in request.parsed_obj['client_info'].keys():
            macro_goal = LookupMacroGoals.query.filter_by(goal_id=request.parsed_obj['client_info']['primary_macro_goal_id']).one_or_none()
            if not macro_goal:
                raise InputError(400, 'Invalid primary_macro_goal_id')
        
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
        client_info = request.parsed_obj['client_info']
        if client_info:
            if 'race_information' in client_info:
                #send race_information through race-and-ethnicity endpoint
                if client_info['race_information']['mother']:
                    mother = client_info['race_information']['mother']
                else:
                    mother = None
                if client_info['race_information']['father']:
                    father = client_info['race_information']['father']
                else:
                    father = None

                process_race_and_ethnicity(user_id, mother, father)
                del client_info['race_information']
                
            client_data.update(request.parsed_obj['client_info'])
        if request.parsed_obj['user_info']:
            user_data.update(request.parsed_obj['user_info'])

        db.session.commit()

        # prepare client_info payload  
        client_info_payload = client_data.__dict__
        client_info_payload["primary_goal"] = db.session.query(LookupGoals.goal_name).filter(client_data.primary_goal_id == LookupGoals.goal_id).one_or_none()
        client_info_payload['primary_macro_goal'] = db.session.query(LookupMacroGoals.goal).filter(client_data.primary_macro_goal_id == LookupMacroGoals.goal_id).one_or_none()
        client_info_payload["race_information"] = db.session.query(ClientRaceAndEthnicity.is_client_mother, LookupRaces.race_id, LookupRaces.race_name) \
            .join(LookupRaces, LookupRaces.race_id == ClientRaceAndEthnicity.race_id) \
            .filter(ClientRaceAndEthnicity.user_id == user_id).all()

        #validate territory_id if supplied
        if 'territory_id' in request.parsed_obj['client_info'].keys():
            territory_id = request.parsed_obj['client_info']['territory_id']
            territory = LookupTerritoriesOfOperations.query.filter_by(idx=territory_id).one_or_none()
            if not territory:
                raise GenericNotFound(f'No territory exists with the territory_id {territory_id}.')

            client_info_payload["country"] = LookupCountriesOfOperations.query.filter_by(idx=territory.country_id).one_or_none().country
            client_info_payload['territory'] = territory.sub_territory
            client_info_payload['territory_abbreviation'] = territory.sub_territory_abbreviation
        
        #Not returning profile picture since it can't be edited through PUT

        return {'client_info': client_info_payload, 'user_info': user_data}

@ns.route('/summary/<int:user_id>/')
class ClientSummary(BaseResource):
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
@ns.deprecated
@ns.doc(params={'page': 'request page for paginated clients list',
                'per_page': 'number of clients per page',
                'firstname': 'first name to search',
                'lastname': 'last name to search',
                'email': 'email to search',
                'phone': 'phone number to search',
                'dob': 'date of birth to search',
                'record_locator_id': 'record locator id to search'})
class ClientsDepricated(BaseResource):
    @token_auth.login_required
    @responds(schema=ClientSearchOutSchema, api=ns)
    #@responds(schema=UserSchema(many=True), api=ns)
    def get(self):
        """[DEPRECATED] returns list of clients given query parameters"""
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
class Clients(BaseResource):
    @ns.doc(params={'_from': 'starting at result 0, from what result to display',
                'per_page': 'number of clients per page',
                'firstname': 'first name to search',
                'lastname': 'last name to search',
                'email': 'email to search',
                'phone': 'phone number to search',
                'dob': 'date of birth to search',
                'modobio_id': 'modobio id to search'})
    @token_auth.login_required(user_type=('staff',))
    @responds(schema=ClientSearchOutSchema, api=ns)
    def get(self):
        """returns list of clients given query parameters,"""
        #if ELASTICSEARCH_URL isn't set, the search request will return without doing anything
        es = current_app.elasticsearch
        if not es: return

        current_user,_ = token_auth.current_user()
        # bring up user_ids for care team members
        care_team_ids = db.session.execute(select(
            ClientClinicalCareTeam.user_id
        ).where(
            ClientClinicalCareTeam.team_member_user_id==current_user.user_id)
        ).scalars().all()

        # no care team members
        if len(care_team_ids) == 0:
            return {'items': []}

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
            body={"query":{"bool":{"must":{"multi_match":{"query": search.strip(), "fuzziness":"AUTO:1,2", "zero_terms_query": "all"}},"filter":[{"term":{"dob":param.get('dob')}},{"terms":{"user_id": [f"{id_}" for id_ in care_team_ids]} } ] }},"from":startAt,"size":per_page}
        else:
            body={"query":{"bool":{"must":{"multi_match":{"query": search.strip(), "fuzziness": "AUTO:1,2" ,"zero_terms_query": "all"}},"filter":{"terms":{"user_id":[str(_id) for _id in care_team_ids]}}}},"from":startAt,"size":per_page}
        
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
                '_self': url_for('api.client_clients', _from=startAt, per_page=per_page),
                '_next': url_for('api.client_clients', _from=startAt + per_page, per_page=per_page)
                if startAt + per_page < total_hits else None,
                '_prev': url_for('api.client_clients', _from= startAt-per_page if startAt-per_page >=0 else 0, per_page=per_page)
                if startAt != 0 else None,
            }, 
            'items': items}
        
        #TODO maybe elasticsarch-DSL
        #This search works by searching the input fields and making a few changes in case of a typo, but
        #will only return exact matches for input strings of length one or two 
        return response

@ns.route('/consent/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ConsentContract(BaseResource):
    """client consent forms"""
    @token_auth.login_required
    @responds(schema=ClientConsentSchema, api=ns)
    def get(self, user_id):
        """returns the most recent consent table as a json for the user_id specified"""
        super().check_user(user_id, user_type='client')

        client_consent_form = ClientConsent.query.filter_by(user_id=user_id).order_by(ClientConsent.idx.desc()).first()
        
        if not client_consent_form:
            raise ContentNotFound()

        return client_consent_form

    @accepts(schema=ClientConsentSchema, api=ns)
    @token_auth.login_required
    @responds(schema=ClientConsentSchema, status_code=201, api=ns)
    def post(self, user_id):
        """ Create client consent contract for the specified user_id """
        super().check_user(user_id, user_type='client')

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
class ReleaseContract(BaseResource):
    """Client release forms"""

    @token_auth.login_required
    @responds(schema=ClientReleaseSchema, api=ns)
    def get(self, user_id):
        """returns most recent client release table as a json for the user_id specified"""
        super().check_user(user_id, user_type='client')

        client_release_contract =  ClientRelease.query.filter_by(user_id=user_id).order_by(ClientRelease.idx.desc()).first()

        if not client_release_contract:
            raise ContentNotFound()

        return client_release_contract

    @accepts(schema=ClientReleaseSchema)
    @token_auth.login_required
    @responds(schema=ClientReleaseSchema, status_code=201, api=ns)
    def post(self, user_id):
        """create client release contract object for the specified user_id"""
        super().check_user(user_id, user_type='client')

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
class PoliciesContract(BaseResource):
    """Client policies form"""

    @token_auth.login_required
    @responds(schema=ClientPoliciesContractSchema, api=ns)
    def get(self, user_id):
        """returns most recent client policies table as a json for the user_id specified"""
        super().check_user(user_id, user_type='client')

        client_policies =  ClientPolicies.query.filter_by(user_id=user_id).order_by(ClientPolicies.idx.desc()).first()

        if not client_policies:
            raise ContentNotFound()
        return  client_policies

    @accepts(schema=ClientPoliciesContractSchema, api=ns)
    @token_auth.login_required
    @responds(schema=ClientPoliciesContractSchema, status_code= 201, api=ns)
    def post(self, user_id):
        """create client policies contract object for the specified user_id"""
        super().check_user(user_id, user_type='client')

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
class ConsultConstract(BaseResource):
    """client consult contract"""

    @token_auth.login_required
    @responds(schema=ClientConsultContractSchema, api=ns)
    def get(self, user_id):
        """returns most recent client consultation table as a json for the user_id specified"""
        super().check_user(user_id, user_type='client')

        client_consult =  ClientConsultContract.query.filter_by(user_id=user_id).order_by(ClientConsultContract.idx.desc()).first()

        if not client_consult:
            raise ContentNotFound()
        return client_consult

    @accepts(schema=ClientConsultContractSchema, api=ns)
    @token_auth.login_required
    @responds(schema=ClientConsultContractSchema, status_code= 201, api=ns)
    def post(self, user_id):
        """create client consult contract object for the specified user_id"""
        super().check_user(user_id, user_type='client')

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
class SubscriptionContract(BaseResource):
    """client subscription contract"""

    @token_auth.login_required
    @responds(schema=ClientSubscriptionContractSchema, api=ns)
    def get(self, user_id):
        """returns most recent client subscription contract table as a json for the user_id specified"""
        super().check_user(user_id, user_type='client')

        client_subscription =  ClientSubscriptionContract.query.filter_by(user_id=user_id).order_by(ClientSubscriptionContract.idx.desc()).first()
        if not client_subscription:
            raise ContentNotFound()
        return client_subscription

    @accepts(schema=SignAndDateSchema, api=ns)
    @token_auth.login_required
    @responds(schema=ClientSubscriptionContractSchema, status_code= 201, api=ns)
    def post(self, user_id):
        """create client subscription contract object for the specified user_id"""
        super().check_user(user_id, user_type='client')

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
class IndividualContract(BaseResource):
    """client individual services contract"""

    @token_auth.login_required
    @responds(schema=ClientIndividualContractSchema, api=ns)
    def get(self, user_id):
        """returns most recent client individual servies table as a json for the user_id specified"""
        super().check_user(user_id, user_type='client')
        
        client_services =  ClientIndividualContract.query.filter_by(user_id=user_id).order_by(ClientIndividualContract.idx.desc()).first()

        if not client_services:
            raise ContentNotFound()
        return  client_services

    @token_auth.login_required
    @accepts(schema=ClientIndividualContractSchema, api=ns)
    @responds(schema=ClientIndividualContractSchema,status_code=201, api=ns)
    def post(self, user_id):
        """create client individual services contract object for the specified user_id"""
        super().check_user(user_id, user_type='client')

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
class SignedDocuments(BaseResource):
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
        super().check_user(user_id, user_type='client')

        urls = {}
        paths = []

        s3 = boto3.client('s3')
        params = {
            'Bucket': current_app.config['AWS_S3_BUCKET'],
            'Key': None}

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
                .first())
            if result and result.pdf_path:
                paths.append(result.pdf_path)

                params['Key'] = result.pdf_path
                url = s3.generate_presigned_url('get_object', Params=params, ExpiresIn=600)
                urls[table.displayname] = url

        concat = merge_pdfs(paths, user_id)
        urls['All documents'] = concat

        return {'urls': urls}

@ns.route('/registrationstatus/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class JourneyStatusCheck(BaseResource):
    """
        Returns the outstanding forms needed to complete the client journey
    """
    @responds(schema=ClientRegistrationStatusSchema, api=ns)
    @token_auth.login_required
    def get(self, user_id):
        """
        Returns the client's outstanding registration items and their URIs.
        """
        super().check_user(user_id, user_type='client')

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
class TestEmail(BaseResource):
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
class ClientDataStorageTiers(BaseResource):
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
class ClientToken(BaseResource):
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
    @ns.deprecated
    @token_auth.login_required(user_type=('client',))
    def delete(self):
        """
        Deprecated 11.19.20..does nothing now
        invalidate urrent token. Used to effectively logout a user
        """
        return '', 200


@ns.route('/clinical-care-team/members/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ClinicalCareTeamMembers(BaseResource):
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
        member's email. Clients may only have 20 team members stored (not including temporary). 

        Emails are checked against the database. If the email is associated with a current user, 
        the user's id is stored in the ClientClinicalCareTeam table. Otherwise, just the 
        email address is registered. 

        What if a client adds someone not currently a modobio user:    
            If a user is NOT yet a modobio member, we will use the provided email to create a new user and link
            the current authorization request to that new user. The account will be in an unverified state until that 
            email is used as part of the account creation routine. 


        Parameters
        ----------
        user_id : int
            User ID number

        Expected payload includes
        email : str
            Email of new care team member in case they are not yet a modobio user
        modobio_id : str
            Modobio ID of new care team member
        Returns
        -------
        dict
            Returns the entries into the clinical care team. 
        """
        
        data = request.parsed_obj

        user = token_auth.current_user()[0]

        current_team = db.session.execute(
            select(ClientClinicalCareTeam, User.email, User.modobio_id).
            join(User, User.user_id == ClientClinicalCareTeam.team_member_user_id).
            where(ClientClinicalCareTeam.user_id == user.user_id)
        ).all()

        current_team_emails = [x[1] for x in current_team]
        current_team_modobio_ids = [x[2] for x in current_team]

        # prevent users from having more than 20 clinical care team members
        if len(current_team) + len(data.get("care_team")) > 20:
            raise InputError(message="Attemping to add too many team members", status_code=400)

        # enter new team members into client's clinical care team
        # if email is associated with a current user account, add that user's id to 
        #  the database entry
        for team_member in data.get("care_team"):
            
            if 'modobio_id' not in team_member and 'team_member_email' not in team_member:
                raise InputError(message="Either modobio_id or email must be provided for each care team member", status_code=400)

            # skip if user already part of care team
            elif team_member.get('modobio_id', '').upper() in current_team_modobio_ids or team_member.get('team_member_email','').lower() in current_team_emails:
                continue
            
            # user attempting to add themselves, skip.
            elif team_member.get('modobio_id') == user.modobio_id or team_member.get('team_member_email') == user.email:
                continue

            # if modobio_id has been given, find the user with that id and insert their email into the payload
            elif 'modobio_id' in team_member:
                modo_id = team_member.get('modobio_id', '').upper()
                team_member_user = User.query.filter_by(modobio_id=modo_id).one_or_none()
                if team_member_user:
                    team_member["team_member_user_id"] = team_member_user.user_id
                else:
                    raise UserNotFound(message=f"The user with modobio_id {modo_id} does not exist")
           
            # only email provided. Check if the user exists, if not, create new user
            else:
                team_member_user = User.query.filter_by(email=team_member["team_member_email"].lower()).one_or_none()
                if team_member_user:
                    team_member["team_member_user_id"] = team_member_user.user_id
                # email is not in our system. 
                # create a new, unverified user using the provided email
                # user is neither staff nor client
                else:
                    team_member_user = User(email = team_member['team_member_email'], is_staff=False, is_client=False)
                    db.session.add(team_member_user)
                    db.session.flush()
                    team_member["team_member_user_id"] = team_member_user.user_id
                    
            # add new team member to the clincial care team
            db.session.add(ClientClinicalCareTeam(**{"team_member_user_id": team_member["team_member_user_id"],
                                                    "user_id": user_id})) 

        db.session.commit()

        # prepare response with names for clinical care team members who are also users 
        current_team = []
        current_team_users = db.session.query(
                                    ClientClinicalCareTeam, User
                                ).filter(
                                    ClientClinicalCareTeam.user_id == user_id
                                ).filter(ClientClinicalCareTeam.team_member_user_id == User.user_id
                                ).all()
        fh = FileHandling()

        for team_member in current_team_users:
            staff_roles = None
            membersince = None
            profile_pic = None
            # bring up a profile photo and membersince date for the team member
            staff_profile = db.session.execute(select(
                StaffProfile
            ).where(StaffProfile.user_id == team_member[1].user_id
            )).scalars().one_or_none()

            if staff_profile:
                membersince = staff_profile.membersince
                profile_pic_path = [pic.image_path for pic in staff_profile.profile_pictures if pic.width == 64]                
                profile_pic = (fh.get_presigned_url(file_path=profile_pic_path[0]) if len(profile_pic_path) > 0 else None)
                staff_roles = db.session.execute(select(StaffRoles.role).where(StaffRoles.user_id == team_member[1].user_id)).scalars().all() 
                is_staff = True
            else:
                is_staff = False
                client_profile = db.session.execute(select(
                    ClientInfo
                ).where(
                    ClientInfo.user_id == team_member[0].team_member_user_id
                )).scalars().one_or_none()

                if client_profile:
                    membersince = client_profile.membersince
                    profile_pic_path = [pic.image_path for pic in client_profile.profile_pictures if pic.width == 64]                
                    profile_pic = (fh.get_presigned_url(file_path=profile_pic_path[0]) if len(profile_pic_path) > 0 else None)
            
            #bring up the authorizations this care team member has for the client
            team_member_authorizations = db.session.execute(
                select(ClientClinicalCareTeamAuthorizations, LookupClinicalCareTeamResources.display_name
                ).join(LookupClinicalCareTeamResources, LookupClinicalCareTeamResources.resource_id == ClientClinicalCareTeamAuthorizations.resource_id
                ).where(
                    ClientClinicalCareTeamAuthorizations.user_id == user_id,
                    ClientClinicalCareTeamAuthorizations.team_member_user_id == team_member[1].user_id
                    )
            ).all()

            authorizations = [{'resource_id': auth.resource_id, 'status': auth.status, 'display_name': display_name} for auth, display_name in team_member_authorizations]


            current_team.append({
                'firstname': team_member[1].firstname,
                'lastname': team_member[1].lastname, 
                'modobio_id': team_member[1].modobio_id,
                'team_member_email': team_member[1].email,
                'team_member_user_id':team_member[0].team_member_user_id,
                'profile_picture': profile_pic,
                'staff_roles' : staff_roles,
                'is_temporary': team_member[0].is_temporary,
                'membersince': membersince,
                'is_staff': is_staff,
                'authorizations': authorizations
            })
        
        response = {"care_team": current_team,
                    "total_items": len(current_team) }

        return response

    @token_auth.login_required(user_type=('client',))
    @accepts(schema=ClientClinicalCareTeamDeleteSchema, api=ns)
    def delete(self, user_id):
        """
        Remove members of a client's clinical care team using the team member's email address.
        Any matches between the incoming payload and current team members in the DB will be removed. 

        Parameters
        ----------
        user_id : int
            User ID number

        Expected payload includes
        team_member_user_id : int

        Returns
        -------
        200 OK
        """
        
        data = request.parsed_obj
       

        for team_member in data.get("care_team"):
            # TODO remove one of these authorization table in a followup story
            ClientClinicalCareTeamAuthorizations.query.filter_by(user_id=user_id, team_member_user_id = team_member.get('team_member_user_id')).delete()
            ClientClinicalCareTeam.query.filter_by(user_id=user_id, team_member_user_id = team_member.get('team_member_user_id')).delete()
            
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
        # prepare response with names for clinical care team members who are also users 
        current_team = []
        current_team_users = db.session.query(
                                    ClientClinicalCareTeam, User
                                ).filter(
                                    ClientClinicalCareTeam.user_id == user_id
                                ).filter(ClientClinicalCareTeam.team_member_user_id == User.user_id
                                ).all()
        fh = FileHandling()

        for team_member in current_team_users:
            staff_roles = None
            membersince = None
            profile_pic = None
            # bring up a profile photo and membersince date for the team member
            staff_profile = db.session.execute(select(
                StaffProfile
            ).where(StaffProfile.user_id == team_member[1].user_id
            )).scalars().one_or_none()

            if staff_profile:
                membersince = staff_profile.membersince
                profile_pic_path = [pic.image_path for pic in staff_profile.profile_pictures if pic.width == 64]                
                profile_pic = (fh.get_presigned_url(file_path=profile_pic_path[0]) if len(profile_pic_path) > 0 else None)
                staff_roles = db.session.execute(select(StaffRoles.role).where(StaffRoles.user_id == team_member[1].user_id)).scalars().all() 
                is_staff = True
            else:
                is_staff = False
                client_profile = db.session.execute(select(
                    ClientInfo
                ).where(
                    ClientInfo.user_id == team_member[0].team_member_user_id
                )).scalars().one_or_none()

                if client_profile:
                    membersince = client_profile.membersince
                    profile_pic_path = [pic.image_path for pic in client_profile.profile_pictures if pic.width == 64]                
                    profile_pic = (fh.get_presigned_url(file_path=profile_pic_path[0]) if len(profile_pic_path) > 0 else None)
                
            #bring up the authorizations this care team member has for the client
            team_member_authorizations = db.session.execute(
                select(ClientClinicalCareTeamAuthorizations, LookupClinicalCareTeamResources.display_name
                ).join(LookupClinicalCareTeamResources, LookupClinicalCareTeamResources.resource_id == ClientClinicalCareTeamAuthorizations.resource_id
                ).where(
                    ClientClinicalCareTeamAuthorizations.user_id == user_id,
                    ClientClinicalCareTeamAuthorizations.team_member_user_id == team_member[1].user_id
                    )
            ).all()

            authorizations = [{'resource_id': auth.resource_id, 'status': auth.status, 'display_name': display_name} for auth, display_name in team_member_authorizations]

            member_data = {
                'firstname': team_member[1].firstname,
                'lastname': team_member[1].lastname, 
                'modobio_id': team_member[1].modobio_id,
                'team_member_email': team_member[1].email,
                'team_member_user_id':team_member[0].team_member_user_id,
                'profile_picture': profile_pic,
                'staff_roles' : staff_roles,
                'is_temporary': team_member[0].is_temporary,
                'membersince': membersince,
                'is_staff': is_staff,
                'authorizations' : authorizations
            }

            #calculate how much time is remaining for temporary members
            if team_member[0].is_temporary:
                expire_date = team_member[0].created_at + timedelta(hours=180)
                time_remaining = expire_date - datetime.utcnow()
                member_data['days_remaining'] = time_remaining.days
                member_data['hours_remaining'] = time_remaining.seconds//3600


            current_team.append(member_data)
        
        response = {"care_team": current_team,
                    "total_items": len(current_team) }

        return response

@ns.route('/clinical-care-team/members/temporary/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ClinicalCareTeamTemporaryMembers(BaseResource):
    """
    Endpoints related to temporary care team members.
    Temporary members are not considered in a user's maximum allowed team members limit (20).
    They will lose access 180 hours after having been added to a user's care team.
    """
    @token_auth.login_required
    @accepts(schema=ClinicalCareTeamTemporaryMembersSchema, api=ns)
    @responds(schema=ClientClinicalCareTeamSchema, api=ns, status_code=201)
    def post(self, user_id):
        """
        Adds a practitioner as a temporary team member to a user's care team
        """
        super().check_user(user_id, user_type='client')

        #assure that a booking exists for the given booking_id and that it is between the given client
        #and staff user ids
        if not TelehealthBookings.query.filter_by(idx=request.parsed_obj['booking_id'], 
                staff_user_id=request.parsed_obj['staff_user_id'],
                client_user_id=user_id).one_or_none():
            raise InputError(message="The booking id given does not exist or is not the correct booking id" \
                " for the given client and staff user_ids.", status_code=400)

        #ensure that this client does not already have this user as a care team member
        staff_user_id=request.parsed_obj['staff_user_id']
        if ClientClinicalCareTeam.query.filter_by(user_id=user_id, team_member_user_id=staff_user_id).one_or_none():
            raise InputError(message=f'The user with user id {staff_user_id} is already on the care team of the' \
                f'client with the user id {user_id}.')
        #retrieve staff account, staff account must exist because of the above check in the bookings table
        team_member = User.query.filter_by(user_id=request.parsed_obj['staff_user_id']).one_or_none()

        db.session.add(ClientClinicalCareTeam(**{"team_member_user_id": team_member.user_id,
                                            "user_id": user_id,
                                            "is_temporary": True}))

        db.session.commit()

        current_team = ClientClinicalCareTeam.query.filter_by(user_id=user_id, team_member_user_id=None).all()

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

        return {"care_team": current_team, "total_items": len(current_team)}

    @token_auth.login_required
    @ns.doc(params={'team_member_user_id': 'User id of the member to make permanent.'})
    @responds(schema=ClientClinicalCareTeamSchema, api=ns, status_code=201)
    def put(self, user_id):
        """
        Update a temporary team member to a permanent team member
        """
        target_id = request.args.get('team_member_user_id', type=int)

        team_member = ClientClinicalCareTeam.query.filter_by(user_id=user_id, team_member_user_id=target_id).one_or_none()

        #if team member exists, change their status to permanent, otherwise raise an error
        if not team_member:
            raise InputError(message=f'The user with user id {target_id} is not on the care team for the client with' \
                f'the user id {user_id}. Please use /client/clinical-care-team/ POST endpoint.')
        else:
            team_member.is_temporary = False
            db.session.commit()

        current_team = ClientClinicalCareTeam.query.filter_by(user_id=user_id, team_member_user_id=None).all()

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

        return {"care_team": current_team, "total_items": len(current_team)}

@ns.route('/clinical-care-team/member-of/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class UserClinicalCareTeamApi(BaseResource):
    """
    Clinical care teams the speficied user is part of
    
    Endpoint for viewing and managing the list of clients who have the specified user as part of their care team.
    """
    @token_auth.login_required(user_type=('staff_self', 'client'))
    @responds(schema=ClinicalCareTeamMemberOfSchema, api=ns, status_code=200)
    def get(self, user_id):
        """
        returns the list of clients whose clinical care team the given user_id
        is a part of along with the permissions granted to them
        """
        res = []
        fh = FileHandling()
        for client in ClientClinicalCareTeam.query.filter_by(team_member_user_id=user_id).all():
            client_user = User.query.filter_by(user_id=client.user_id).one_or_none()
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
            
            profile_pic_path = db.session.execute(
                select(
                    UserProfilePictures.image_path
                ).where(UserProfilePictures.client_id == client_user.user_id, UserProfilePictures.width == 64)
                ).scalars().one_or_none()                
            profile_pic = (fh.get_presigned_url(file_path=profile_pic_path) if profile_pic_path else None)
            res.append({'client_user_id': client_user.user_id, 
                        'client_name': ' '.join(filter(None, (client_user.firstname, client_user.middlename ,client_user.lastname))),
                        'client_email': client_user.email,
                        'client_modobio_id': client_user.modobio_id,
                        'client_profile_picture': profile_pic,
                        'client_added_date': client.created_at,
                        'authorizations': [{'display_name': x[1], 'resource_id': x[0]} for x in authorizations_query]})
        
        return {'member_of_care_teams': res, 'total': len(res)}

from sqlalchemy.exc import SQLAlchemyError
@ns.route('/clinical-care-team/resource-authorization/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ClinicalCareTeamResourceAuthorization(BaseResource):
    """
    Create, update, remove, retrieve authorization of ehr page access for care team members.

    There are 2 contexts which this API can be accessed:
        - client (self): client is editing and viewing their own care team settings
            -POST,GET,PUT,DELETE access
        - staff: staff user is requesting to have resource access
            -POST, limited access

    Client users not accessing their own resource authorization are not allowed to use this endpoint.

    More on staff access:
        Staff may request resource authorization though the POST method. Resource request is logged but not yet verified until the 
        client themselves makes a PUT request to verify the resource access. 
        
    Adding current modobio users to the care team:
        Users must already be part of a client's clinical care team in order to be granted access to resources
        Care team addition can either be done through the client/clinical-care-team/members/<int:user_id>/ POST endpooint
        If a user is not yet part of the client's care team, an error is raised, must POST to /clinical-care-team/members/<int:user_id>/ to add. 


    Care team resources are added by resource_id.    
    The available options can be foundby using the /lookup/care-team/ehr-resources/ (GET) API. 
    """
    @token_auth.login_required(user_type=('client', 'staff'))
    @accepts(schema=ClinicalCareTeamAuthorizationNestedSchema, api=ns)
    @responds(schema=ClinicalCareTeamAuthorizationNestedSchema, api=ns, status_code=201)
    def post(self, user_id):
        """
        Add new clinical care team authorizations for the specified user_id 
        """
        current_user,_ = token_auth.current_user()

        data = request.parsed_obj

        current_team_ids = db.session.query(ClientClinicalCareTeam.team_member_user_id).filter(ClientClinicalCareTeam.user_id==user_id).all()
        current_team_ids = [x[0] for x in current_team_ids if x[0] is not None]
        
        current_authorizations = db.session\
            .query(ClientClinicalCareTeamAuthorizations.team_member_user_id,ClientClinicalCareTeamAuthorizations.resource_id)\
            .filter_by(user_id=user_id).all()

        # validate the requested resource authorizations by checking them against the lookup table
        care_team_resources = LookupClinicalCareTeamResources.query.all()
        care_team_resources_ids = [x.resource_id for x in care_team_resources]
        requested_resources_by_id = [x.resource_id for x in data.get('clinical_care_team_authorization')]

        if len(set(requested_resources_by_id) - set(care_team_resources_ids)) > 0:
            raise InputError(message="a resource_id was not recognized", status_code=400)
      
        # user_id denotes the main users
        # if the current user is not the main user (aka a random user)
        # they must be a staff member requesting access to resources. 
        if current_user.user_id != user_id: 
            # bring up all team_member_ids in payload
            # all team members in resource request must hav ethe same id as logged-in user
            team_member_ids = set([x.team_member_user_id for x in data.get('clinical_care_team_authorization')])

            if current_user.user_id not in team_member_ids or len(team_member_ids) > 1:
                raise InputError(message="cannot request other users be added to care team", status_code=400)
            
            # authorization must be validated by the client themselves
            status = 'pending'
        else:
            # The logged-in user is the main user in this request
            status = 'accepted'
        
        # loop through the authorization requests and add them ``
        for authorization in data.get('clinical_care_team_authorization'):
            if authorization.team_member_user_id in current_team_ids:
                for member_id,resource_id in current_authorizations:
                    if authorization.team_member_user_id == member_id and authorization.resource_id == resource_id:
                        raise InputError(message=f"Member {member_id} and resource {resource_id} have already been requested", status_code=400)

                authorization.user_id = user_id
                authorization.status = status
                db.session.add(authorization)
            else:
                db.session.rollback()
                raise InputError(message="Team member not in care team", status_code=400)
        db.session.commit()
        return 

    @token_auth.login_required(user_type=('client',))
    @responds(schema=ClinicalCareTeamAuthorizationNestedSchema, api=ns, status_code=200)
    def get(self, user_id):
        """
        Retrieve client's clinical care team authorizations
        """

        current_user,_ = token_auth.current_user()

        if current_user.user_id != user_id:
            raise InputError(message="Unauthorized", status_code=401)

        data = db.session.query(
            ClientClinicalCareTeamAuthorizations.resource_id, 
            LookupClinicalCareTeamResources.display_name,
            User.firstname, 
            User.lastname, 
            User.email,
            User.user_id,
            User.modobio_id,
            ClientClinicalCareTeamAuthorizations.status
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
                'team_member_modobio_id': row[6],
                'status': row[7]}

            care_team_auths.append(tmp)
        
        payload = {'clinical_care_team_authorization': care_team_auths}

        return payload

    @token_auth.login_required(user_type=('client',))
    @accepts(schema=ClinicalCareTeamAuthorizationNestedSchema, api=ns)
    @responds(api=ns,status_code=200)
    def put(self, user_id):
        """
        This put request is used to change the status approval from the client to team member from 

        'pending' to 'approved'

        to reject a team member from viewing data, the delete request should be used.
        """
        current_user,_ = token_auth.current_user()

        if current_user.user_id != user_id:
            raise InputError(message="Unauthorized", status_code=401)

        data = request.json

        for dat in data.get('clinical_care_team_authorization'):
            try:
                authorization = ClientClinicalCareTeamAuthorizations.query.filter_by(user_id=user_id,
                                                                                resource_id = dat['resource_id'],
                                                                                team_member_user_id = dat['team_member_user_id']
                                                                                ).one_or_none()
            except SQLAlchemyError as e:
                return e.message

            if not authorization:
                raise InputError(message="Team member or resource ID request not found", status_code=400)
            authorization.update({'status': 'accepted'})

        db.session.commit()
        

    @token_auth.login_required(user_type=('client',))
    @accepts(schema=ClinicalCareTeamAuthorizationNestedSchema, api=ns)
    @responds(status_code=200, api=ns)
    def delete(self, user_id):
        """
        Remove a previously saved authorization. Takes the same payload as the POST method.
        """
        current_user,_ = token_auth.current_user()

        if current_user.user_id != user_id:
            raise InputError(message="Unauthorized", status_code=401)

        data = request.parsed_obj

        for dat in data.get('clinical_care_team_authorization'):
            authorization = ClientClinicalCareTeamAuthorizations.query.filter_by(user_id=user_id,
                                                                                resource_id = dat.resource_id,
                                                                                team_member_user_id = dat.team_member_user_id
                                                                                ).one_or_none()
            if not authorization:
                raise InputError(message="Team member or resource ID request not found", status_code=400)
            
            db.session.delete(authorization)

        db.session.commit()


@ns.route('/drinks/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ClientDrinksApi(BaseResource):
    """
    Endpoints related to nutritional beverages that are assigned to clients.
    """
    @token_auth.login_required(user_type=('staff',), staff_role=('medical_doctor', 'nutritionist'))
    @accepts(schema=ClientAssignedDrinksSchema, api=ns)
    @responds(schema=ClientAssignedDrinksSchema, api=ns, status_code=201)
    def post(self, user_id):
        """
        Add an assigned drink to the client designated by user_id.
        """
        super().check_user(user_id, user_type='client')
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
        super().check_user(user_id, user_type='client')

        return ClientAssignedDrinks.query.filter_by(user_id=user_id).all()
    
    @token_auth.login_required(user_type=('staff',), staff_role=('medical_doctor', 'nutritionist'))
    @accepts(schema=ClientAssignedDrinksDeleteSchema, api=ns)
    @responds(schema=ClientAssignedDrinksSchema, api=ns, status_code=204)
    def delete(self, user_id):
        """
        Delete a drink assignemnt for a user with user_id and drink_id
        """
        super().check_user(user_id, user_type='client')

        for drink_id in request.parsed_obj['drink_ids']:
            drink = ClientAssignedDrinks.query.filter_by(user_id=user_id, drink_id=drink_id).one_or_none()

            if not drink:
                raise ContentNotFound()

            db.session.delete(drink)
        
        db.session.commit()

@ns.route('/mobile-settings/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ClientMobileSettingsApi(BaseResource):
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

        super().check_user(user_id, user_type='client')

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

        super().check_user(user_id, user_type='client')

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

        super().check_user(user_id, user_type='client')

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
class ClientHeightApi(BaseResource):
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
        super().check_user(user_id, user_type='client')

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
        super().check_user(user_id, user_type='client')

        return ClientHeightHistory.query.filter_by(user_id=user_id).all()

@ns.route('/weight/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ClientWeightApi(BaseResource):
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
        super().check_user(user_id, user_type='client')

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
        super().check_user(user_id, user_type='client')

        return ClientWeightHistory.query.filter_by(user_id=user_id).all()

@ns.route('/waist-size/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ClientWaistSizeApi(BaseResource):
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
        super().check_user(user_id, user_type='client')

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
        super().check_user(user_id, user_type='client')

        return ClientWaistSizeHistory.query.filter_by(user_id=user_id).all()

@ns.route('/transaction/history/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ClientTransactionHistoryApi(BaseResource):
    """
    Endpoints related to viewing a client's transaction history.
    """
    @token_auth.login_required(user_type=('client','staff'), staff_role=('client_services',))
    @responds(schema=ClientTransactionHistorySchema(many=True), api=ns, status_code=200)
    def get(self, user_id):
        """
        Returns a list of all transactions for the given user_id.
        """
        super().check_user(user_id, user_type='client')

        return ClientTransactionHistory.query.filter_by(user_id=user_id).all()

@ns.route('/transaction/<int:transaction_id>/')
@ns.doc(params={'transaction_id': 'Transaction ID number'})
class ClientTransactionApi(BaseResource):
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
class ClientTransactionPutApi(BaseResource):
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
        super().check_user(user_id, user_type='client')

        request.parsed_obj.user_id = user_id
        db.session.add(request.parsed_obj)
        db.session.commit()

        return request.parsed_obj

@ns.route('/default-health-metrics/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ClientWeightApi(BaseResource):
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
        super().check_user(user_id, user_type='client')

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

@ns.route('/race-and-ethnicity/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ClientRaceAndEthnicityApi(BaseResource):
    """
    Endpoint for returning viewing and editing informations about a client's race and ethnicity
    information.
    """
    @token_auth.login_required()
    @responds(schema=ClientRaceAndEthnicitySchema(many=True), api=ns, status_code=200)
    def get(self, user_id):
        super().check_user(user_id, user_type='client')

        res = db.session.query(ClientRaceAndEthnicity.is_client_mother, LookupRaces.race_id, LookupRaces.race_name) \
            .join(LookupRaces, LookupRaces.race_id == ClientRaceAndEthnicity.race_id) \
            .filter(ClientRaceAndEthnicity.user_id == user_id).all()
        
        return res

    @token_auth.login_required()
    @accepts(schema=ClientRaceAndEthnicityEditSchema, api=ns)
    @responds(schema=ClientRaceAndEthnicitySchema(many=True), api=ns, status_code=201)
    def put(self, user_id):

        super().check_user(user_id, user_type='client')

        if request.parsed_obj['mother']:
            mother = request.parsed_obj['mother']
        else:
            mother = None
        if request.parsed_obj['father']:
            father = request.parsed_obj['father']
        else:
            father = None

        process_race_and_ethnicity(user_id, mother, father)

        res = db.session.query(ClientRaceAndEthnicity.is_client_mother, LookupRaces.race_id, LookupRaces.race_name) \
            .join(LookupRaces, LookupRaces.race_id == ClientRaceAndEthnicity.race_id) \
            .filter(ClientRaceAndEthnicity.user_id == user_id).all()

        return res



