
from flask import request
from flask_accepts import accepts, responds
from flask_restx import Resource

from odyssey import db
from odyssey.api import api
from odyssey.api.staff.models import StaffOperationalTerritories, StaffRoles, StaffRecentClients
from odyssey.api.user.models import User, UserLogin, UserTokenHistory
from odyssey.utils.auth import token_auth, basic_auth
from odyssey.utils.errors import UnauthorizedUser, StaffEmailInUse
from odyssey.api.user.schemas import UserSchema, StaffInfoSchema
from odyssey.api.staff.schemas import (
    StaffOperationalTerritoriesNestedSchema,
    StaffProfileSchema, 
    StaffRolesSchema,
    StaffRecentClientsSchema,
    StaffTokenRequestSchema
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
    @ns.deprecated
    @token_auth.login_required(user_type=('staff',))
    def delete(self):
        """
        Deprecated 11.23.20..does nothing now
        """
        return '', 200

