from datetime import datetime, timedelta
import secrets

from flask import current_app, request, jsonify
from flask_restx import Resource, fields
from flask_accepts import accepts, responds

from odyssey import db
from odyssey.models.staff import StaffProfile, StaffRoles, StaffRecentClients
from odyssey.models.user import User, UserLogin
from odyssey.api import api
from odyssey.utils.auth import token_auth
from odyssey.api.errors import UnauthorizedUser, StaffEmailInUse, StaffNotFound, ClientNotFound
from odyssey.utils.schemas import (
    StaffInfoSchema,
    StaffProfileSchema, 
    StaffRolesSchema,
    StaffSearchItemsSchema,
    StaffRecentClientsSchema,
    UserSchema
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
    @token_auth.login_required(user_type=('staff_self',))
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

@ns.route('/recentclients/')
class RecentClients(Resource):
    """endpoint related to the staff recent client feature"""
    
    @token_auth.login_required
    @responds(schema=StaffRecentClientsSchema(many=True), api=ns)
    def get(self):
        """get the 10 most recent clients a staff member has loaded"""
        return StaffRecentClients.query.filter_by(staff_user_id=token_auth.current_user()[0].user_id).all()