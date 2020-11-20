from datetime import datetime, timedelta
from flask import current_app, request, jsonify
from flask_restx import Resource
from flask_accepts import accepts, responds
import jwt

from odyssey import db
from odyssey.api.staff.models import StaffProfile, StaffRoles, StaffRecentClients
from odyssey.api.user.models import User, UserLogin
from odyssey.api import api
from odyssey.utils.auth import basic_auth, token_auth
from odyssey.utils.errors import UnauthorizedUser, StaffEmailInUse, StaffNotFound, ClientNotFound, UserNotFound
from odyssey.utils.email import send_email_password_reset
from odyssey.api.user.schemas import UserSchema, StaffInfoSchema
from odyssey.api.staff.schemas import (
    StaffPasswordRecoveryContactSchema, 
    StaffPasswordResetSchema,
    StaffPasswordUpdateSchema,
    StaffProfileSchema, 
    StaffSearchItemsSchema,
    StaffRolesSchema,
    StaffRecentClientsSchema
)
from odyssey.utils.misc import check_client_existence
from werkzeug.security import check_password_hash

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

        # param = {}
        # param_keys = ['firstname', 'lastname', 'email', 'user_id']
        # noMoreSearch = False
        
        # if not request.args:
        #     data = User.query.filter_by(is_staff=True).order_by(Staff.lastname.asc()).all()
        #     noMoreSearch = True
        # elif len(request.args) == 1 and request.args.get('user_id'):
        #     data = [User.query.filter_by(user_id=request.args.get('user_id')).first()]
        #     if not any(data):
        #         raise StaffNotFound(request.args.get('user_id'))
        #     noMoreSearch = True
        
        # if not noMoreSearch:
        #     searchStr = ''
        #     exactMatch = False
        #     for key in param_keys:
        #         param[key] = request.args.get(key, default=None, type=str)
        #         # Cleans up search query
        #         if param[key] is None:
        #             param[key] = ''     
        #         elif key == 'email' and param.get(key, None):
        #             tempEmail = param[key]
        #             param[key] = param[key].replace("@"," ")
        #         searchStr = searchStr + param[key] + ' '
            
        #     data = User.query.whooshee_search(searchStr).all()

        #     # Since email and user_id should be unique, 
        #     # if the input email or user_id exactly matches 
        #     # the profile, only display that user
        #     if param['email']:
        #         for val in data:
        #             if val.email.lower() == tempEmail.lower():
        #                 data = [val]
        #                 exactMatch = True
        #                 break

        #     # Assuming staff will most likely remember their 
        #     # email instead of their staff. If the email is correct
        #     # no need to search through RLI. 
        #     #
        #     # This next check depends on if the whooshee search returns 
        #     # Relevant staff with the correct ID. It is possible for the
        #     # search to return different staff members (and NOT the user_id
        #     # that was a search parameter
        #     #
        #     # If BOTH are incorrect, return data as normal.
        #     if param['user_id'] and not exactMatch:
        #         for val in data:
        #             if val.user_id == param['user_id']:
        #                 data = [val]
        #                 break
        # return data 
    
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
    
@ns.route('/password/forgot-password/recovery-link/')
class PasswordResetEmail(Resource):
    """Password reset endpoints."""
    
    @accepts(schema=StaffPasswordRecoveryContactSchema, api=ns)
    def post(self):
        """begin a password reset session. 
            Staff member unable to log in will request a password reset
            with only their email. Emails will be checked for exact match in the database
            to a staff member. 
    
            If the email exists, a signed JWT is created; encoding the token's expiration 
            time and the user_id. The code will be placed into this URL <url for password reset>
            and sent to a valid email address.  
            If the email does not exist, no email is sent. 
            response 200 OK
        """
        email = request.get_json()['email']

        staff = User.query.filter_by(email=email.lower()).first()
        
        if not email or not staff:
            return 200

        secret = current_app.config['SECRET_KEY']
        encoded_token = jwt.encode({'exp': datetime.utcnow()+timedelta(minutes = 15), 
                                  'sid': staff.user_id}, 
                                  secret, 
                                  algorithm='HS256').decode("utf-8") 
        if current_app.env == "development":
            return jsonify({"token": encoded_token})
        else:
            send_email_password_reset(staff.email, encoded_token)
            return 200
        

@ns.route('/password/forgot-password/reset')
@ns.doc(params={'reset_token': "token from password reset endpoint"})
class ResetPassword(Resource):
    """Reset the user's password."""

    @accepts(schema=StaffPasswordResetSchema, api=ns)
    def put(self):
        """
            Change the current password to the one given
            in the body of this request
            response 200 OK
       """
        # decode and validate token 
        secret = current_app.config['SECRET_KEY']
        reset_token=request.args.get("reset_token")
        try:
            decoded_token = jwt.decode(reset_token, secret, algorithms='HS256')
        except jwt.ExpiredSignatureError:
            raise UnauthorizedUser(message="Token authorization expired")

        # bring up the staff member and reset their password
        pswd = request.get_json()['password']

        staff = UserLogin.query.filter_by(user_id=decoded_token['sid']).first()
        staff.set_password(pswd)

        db.session.commit()

        return 200

@ns.route('/password/update/')
class ChangePassword(Resource):
    """Reset the user's password."""
    @token_auth.login_required
    @accepts(schema=StaffPasswordUpdateSchema, api=ns)
    def post(self):
        """
            Change the current password to the one given
            in the body of this request
            response 200 OK
        """

        data = request.get_json()
        # bring up the staff member and reset their password
        _, user_login = token_auth.current_user()

        if user_login.check_password(password=data["current_password"]):
            user_login.set_password(data["new_password"])
        else:
            raise UnauthorizedUser(message="please enter the correct current password \
                                      otherwise, visit the password recovery endpoint \
                                      /staff/password/forgot-password/recovery-link")
        db.session.commit()

        return 200

@ns.route('/recentclients/')
class RecentClients(Resource):
    """endpoint related to the staff recent client feature"""
    
    @token_auth.login_required
    @responds(schema=StaffRecentClientsSchema(many=True), api=ns)
    def get(self):
        """get the 10 most recent clients a staff member has loaded"""
        return StaffRecentClients.query.filter_by(staff_user_id=token_auth.current_user()[0].user_id).all()


""" Staff Token Endpoint """

@ns.route('/token/')
class StaffToken(Resource):
    """create and revoke tokens"""
    @ns.doc(security='password')
    @basic_auth.login_required(user_type=['staff'])
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
        return {'email': user.email, 
                'firstname': user.firstname, 
                'lastname': user.lastname, 
                'token': user_login.get_token(),
                'user_id': user.user_id,
                'access_roles': [item[0] for item in access_roles]}, 201

    @ns.doc(security='password')
    @token_auth.login_required(user_type=['staff'])
    def delete(self):
        """invalidate current token. Used to effectively logout a user"""
        token_auth.current_user()[1].revoke_token()
        return '', 204
