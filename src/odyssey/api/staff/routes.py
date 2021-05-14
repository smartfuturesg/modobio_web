import os, boto3, secrets, pathlib

from flask import request, current_app, Response
from flask_accepts import accepts, responds
from flask_restx import Resource

from odyssey import db
from odyssey.api import api
from odyssey.api.staff.models import StaffOperationalTerritories, StaffRoles, StaffRecentClients, StaffProfile
from odyssey.api.user.models import User, UserLogin, UserTokenHistory
from odyssey.utils.auth import token_auth, basic_auth
from odyssey.utils.errors import UnauthorizedUser, StaffEmailInUse, InputError
from odyssey.utils.misc import check_staff_existence
from odyssey.utils.constants import ALLOWED_IMAGE_TYPES
from odyssey.api.user.schemas import UserSchema, StaffInfoSchema
from odyssey.api.staff.schemas import (
    StaffOperationalTerritoriesNestedSchema,
    StaffProfileSchema, 
    StaffRolesSchema,
    StaffRecentClientsSchema,
    StaffTokenRequestSchema,
    StaffProfilePageGetSchema
)

ns = api.namespace('staff', description='Operations related to staff members')

@ns.route('/')
#@ns.doc(params={'firstname': 'first name to search',
#                'lastname': 'last name to search',
#                'user_id': 'user_id to search',
#                'email': 'email to search'})
class StaffMembers(Resource):
    """staff member class for creating, getting staff"""
    
    @token_auth.login_required
    #@responds(schema=StaffSearchItemsSchema(many=True), api=ns)
    @responds(schema=UserSchema(many=True), api=ns)
    def get(self):
        """returns list of staff members given query parameters"""                
        # These payload keys should be the same as what's indexed in 
        # the model.
        return User.query.filter_by(is_staff=True)

    
    @token_auth.login_required
    @accepts(schema=StaffProfileSchema, api=ns)
    @responds(schema=StaffProfileSchema, status_code=201, api=ns)     
    def post(self):
        """register a new staff member"""
        data = request.get_json() or {}
        #check if this email is already being used. If so raise 409 conflict error 
        staff = User.query.filter_by(email=data.get('email')).first()
        if staff:
            raise StaffEmailInUse(email=data.get('email'))

        ## TODO: rework Role suppression
        # system_admin: permisison to create staff admin.
        # staff_admin:  can create all other roles except staff/systemadmin
        # if data.get('is_system_admin'):
        #     raise UnauthorizedUser(message=f"Staff member with email {token_auth.current_user()[0].email} is unauthorized to create a system administrator role.")

        # if data.get('is_admin') and token_auth.current_user()[0].get_admin_role() != 'sys_admin':
        #     raise UnauthorizedUser(message=f"Staff member with email {token_auth.current_user()[0].email} is unauthorized to create a staff administrator role. \
        #                          Please contact system admin")
   
        #remove user data from staff data
        user_data = {'email': data['email'], 'password': data['password']}
        del data['email']
        del data['password']

        # Staff schema instance load from payload
        staff_schema = StaffProfileSchema()
        new_staff = staff_schema.load(data)

        db.session.add(new_staff)
        db.session.commit()

        user_data['user_id'] = new_staff.user_id
        new_user = UserSchema().load(user_data)
        
        db.session.add(new_user)
        db.session.commit()

        return new_staff

@ns.route('/roles/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class UpdateRoles(Resource):
    """
    View and update roles for staff member with a given user_id
    """
    @token_auth.login_required
    @accepts(schema=StaffInfoSchema, api=ns)
    @responds(status_code=201, api=ns)   
    def post(self, user_id):
        staff_user, _ = token_auth.current_user()

        # staff are only allowed to edit their own info
        if staff_user.user_id != user_id:
            raise UnauthorizedUser(message="")
        
        data = request.get_json()
        staff_roles = db.session.query(StaffRoles.role).filter(StaffRoles.user_id==user_id).all()
        staff_roles = [x[0] for x in staff_roles]
        staff_role_schema = StaffRolesSchema()

        # loop through submitted roles, add role if not already in db
        for role in data['access_roles']:
            if role not in staff_roles:
                db.session.add(staff_role_schema.load(
                    {'user_id': user_id, 
                    'role': role}))
        
        db.session.commit()
        
        return

    @token_auth.login_required
    @responds(schema=StaffRolesSchema(many=True), status_code=200, api=ns)   
    def get(self, user_id):
        """
        Get staff roles
        """
        staff_user, _ = token_auth.current_user()
       
        staff_roles = StaffRoles.query.filter_by(user_id = user_id)

        return staff_roles

@ns.route('/operational-territories/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class OperationalTerritories(Resource):
    """
    View and update operational territories for staff member with a given user_id
    """
    @token_auth.login_required(user_type=('staff_self',))
    @accepts(schema=StaffOperationalTerritoriesNestedSchema, api=ns)
    @responds(schema = StaffOperationalTerritoriesNestedSchema, status_code=201, api=ns)   
    def post(self, user_id):
        staff_user, _ = token_auth.current_user()

        # staff are only allowed to edit their own info
        if staff_user.user_id != user_id:
            raise UnauthorizedUser(message="")
        data = request.parsed_obj
        # current operational territories
        current_territories = db.session.query(
                        StaffOperationalTerritories.role_id, StaffOperationalTerritories.operational_territory_id
                        ).filter(
                            StaffOperationalTerritories.user_id==user_id
                        ).all()

        # ids of current roles held by staff member             
        current_role_ids = db.session.query(
                        StaffRoles.idx
                        ).filter(
                            StaffRoles.user_id == user_id
                        ).all()
        current_role_ids = [x[0] for x in current_role_ids]

        for territory in data["operational_territories"]:
            # check if role-territory combination already exists. if so, skip it
            if not (territory.role_id, territory.operational_territory_id) in current_territories:
                # ensure role_id is assigned to this staff member
                if territory.role_id in current_role_ids:
                    territory.user_id = user_id
                    db.session.add(territory)
                else:
                    db.session.rollback()
                    raise UnauthorizedUser(message="the staff member does not have this role")

        db.session.commit()
        
        # current operational territories
        current_territories = db.session.query(
                        StaffOperationalTerritories.role_id, StaffOperationalTerritories.operational_territory_id
                        ).filter(
                            StaffOperationalTerritories.user_id==user_id
                        ).all()

        return {"operational_territories": current_territories}

    @token_auth.login_required
    @responds(schema = StaffOperationalTerritoriesNestedSchema, status_code=200, api=ns)   
    def get(self, user_id):
        """
        Responds with current operational territories for each role a staff user
        has assumed
        """
        # current operational territories
        current_territories = db.session.query(
                        StaffOperationalTerritories.role_id, StaffOperationalTerritories.operational_territory_id
                        ).filter(
                            StaffOperationalTerritories.user_id==user_id
                        ).all()
        return {"operational_territories": current_territories}

    @token_auth.login_required(user_type=('staff_self',))
    @accepts(schema=StaffOperationalTerritoriesNestedSchema, api=ns)
    @responds(schema = StaffOperationalTerritoriesNestedSchema, status_code=204, api=ns)   
    def delete(self, user_id):
        """
        Uses the same payload as the POST request on this endpoint to delete 
        entries to the operational territories database.
        """
        data = request.parsed_obj

        for territory in data["operational_territories"]:
            StaffOperationalTerritories.query.filter_by(
                                                    user_id=user_id
                                                ).filter_by(
                                                    operational_territory_id = territory.operational_territory_id
                                                ).filter_by(
                                                    role_id = territory.role_id
                                                ).delete()
        
        db.session.commit()

        return 
    

@ns.route('/recentclients/')
class RecentClients(Resource):
    """endpoint related to the staff recent client feature"""
    
    @token_auth.login_required
    @responds(schema=StaffRecentClientsSchema(many=True), api=ns)
    def get(self):
        """get the 10 most recent clients a staff member has loaded"""
        return StaffRecentClients.query.filter_by(user_id=token_auth.current_user()[0].user_id).all()

""" Staff Token Endpoint """

@ns.route('/token/')
class StaffToken(Resource):
    """create and revoke tokens"""
    @ns.doc(security='password')
    @basic_auth.login_required(user_type=('staff',), email_required=False)
    @responds(schema=StaffTokenRequestSchema, status_code=201, api=ns)
    def post(self):
        """generates a token for the 'current_user' immediately after password authentication"""
        user, user_login = basic_auth.current_user()
        if not user:
            return 401
        # bring up list of staff roles
        access_roles = db.session.query(
                                StaffRoles.role
                            ).filter(
                                StaffRoles.user_id==user.user_id
                            ).all()

        access_token = UserLogin.generate_token(user_type='staff', user_id=user.user_id, token_type='access')
        refresh_token = UserLogin.generate_token(user_type='staff', user_id=user.user_id, token_type='refresh')

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
                'access_roles': [item[0] for item in access_roles],
                'email_verified': user.email_verified}


    @ns.doc(security='password')
    @token_auth.login_required(user_type=('staff',))
    def delete(self):
        """
        Deprecated 11.23.20..does nothing now
        """
        return '', 200

@ns.route('/profile/<int:user_id>/')
class StaffProfilePage(Resource):
    """endpoint related staff members' profile pages"""

    #@token_auth.login_required
    @responds(schema=StaffProfilePageGetSchema, api=ns, status_code=200)
    def get(self, user_id):
        """get details for a staff member's profile page"""
        #ensure this user id is for a valid staff member
        check_staff_existence(user_id)

        user = User.query.filter_by(user_id=user_id).one_or_none()

        res = {
            'firstname': user.firstname,
            'middlename': user.middlename,
            'lastname': user.lastname,
            'biological_sex_male': user.biological_sex_male
        }

        #as long as a staff member exists(checked above), they have a profile 
        #because it is made for them when the staff user is created
        profile = StaffProfile.query.filter_by(user_id=user_id).one_or_none()

        res['bio'] = profile.bio

        #get presigned link to this user's profile picture
        if not current_app.config['LOCAL_CONFIG']:
            s3key = profile.profile_picture
            if s3key != None:
                s3 = boto3.resource('s3')
                params = {
                    'Bucket' : current_app.config['S3_BUCKET_NAME'],
                    'Key' : s3key
                }

                url = boto3.client('s3').generate_presigned_url('get_object', Params=params, ExpiresIn=3600)
                
                res['profile_picture'] = url
            else:
                res['profile_picture'] = None

        return res

    @token_auth.login_required(user_type=('staff_self',))
    @responds(schema=StaffProfilePageGetSchema, api=ns, status_code=200)
    def put(self, user_id):
        """Edit details for a staff member's profile page. 
        
        Expects form data

        "firstname": "string"
        "middlename": "string",
        "lastname": "string",
        "biological_sex_male": "boolean",
        "bio": "string",
        "profile_picture": file (allowed types are '.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp', '.psd', '.pdf')
        """

        #ensure this user id is for a valid staff member
        check_staff_existence(user_id)

        user = User.query.filter_by(user_id=user_id).one_or_none()
        profile = StaffProfile.query.filter_by(user_id=user_id).one_or_none()

        user_update = {}

        #stored here so we know if bio should be returned with the payload
        #we don't want it returned in the key wasn't provided in the request
        bio = None

        for key in request.form:
            if key == 'bio':
                bio = request.form.get('bio')
                profile.bio = bio
            else:
                data = request.form.get(key)
                if key == 'biological_sex_male':
                    #check that this value can be interpretted as a bool
                    if data in ('true', 'True', '1'):
                        data = True
                    elif data in ('false', 'False', '0'):
                        data = False
                    else:
                        raise InputError(422, f'{key} must be a boolean. Acceptable values are \'true\', \'false\', \'True\', \'False\', \'1\', and \'0\'')
                user_update[key] = data

        url = None
        
        #get profile picture and store in s3
        if not current_app.config['LOCAL_CONFIG']:
            if 'profile_picture' in request.files:
                s3 = boto3.resource('s3')
                bucket = s3.Bucket(current_app.config['S3_BUCKET_NAME'])

                #will delete anything starting with this prefix if it exists
                #if nothing matches the prefix, nothing will happen
                bucket.objects.filter(Prefix=f'id{user_id:05d}/profile_picture').delete()

                #implemented as a loop to allow for multiple pictures if needed in the future
                for i, img in enumerate(request.files.getlist('profile_picture')):
                    #Verifying image size is within a safe threashold (MAX = 500 mb)
                    img.seek(0, os.SEEK_END)
                    img_size = img.tell()
                    if img_size > 524288000:
                        raise InputError(413, 'File too large')

                    #make sure this is not an empty file
                    if img_size > 0:
                        #check that file type is one of the allowed image types
                        img_extension = pathlib.Path(img.filename).suffix
                        if img_extension not in ALLOWED_IMAGE_TYPES:
                            raise InputError(422, f'{img_extension} is not an allowed file type. Allowed types are {ALLOWED_IMAGE_TYPES}')

                        #Rename image (format: profile_files/id{user_id:05d}/profile_picture_4digitRandomHex.img_extension) AND Save=>S3
                        img.seek(0)
                        hex_token = secrets.token_hex(4)
                        s3key = f'id{user_id:05d}/profile_picture_{hex_token}{img_extension}'
                        bucket.put_object(Key= s3key, Body=img.stream)

                        profile.profile_picture = s3key

                        #get presigned url to return in response
                        params = {
                            'Bucket' : current_app.config['S3_BUCKET_NAME'],
                            'Key' : s3key
                        }

                        url = boto3.client('s3').generate_presigned_url('get_object', Params=params, ExpiresIn=3600)

                    #exit loop if more than allowed number of images were given
                    if i >= 0:
                        break

        #update user in db
        user.update(user_update)
        
        #add profile keys to user_update to match @responds
        if bio:
            user_update['bio'] = profile.bio
        if url:
            user_update['profile_picture'] = url
        else:
            #profile_picture key was provided with no file. Since this means profile picture was
            #deleted from s3, remove the reference to it from db.
            profile.profile_picture = None

        db.session.commit()

        if len(user_update.keys()) == 0:
            #request was successful but there is no body to return
            return Response(status=204)
        else:
            return user_update