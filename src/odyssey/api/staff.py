from flask import request
from flask_restx import Resource, fields
from flask_accepts import accepts , responds

from odyssey import db
from odyssey.models.main import Staff
from odyssey.api import api
from odyssey.api.auth import token_auth
from odyssey.api.errors import UnauthorizedUser, StaffEmailInUse
from odyssey.api.serializers import new_staff_member
from odyssey.api.schemas import StaffSchema

ns = api.namespace('staff', description='Operations related to staff members')


@ns.route('/')
class StaffMembers(Resource):
    """staff member class for creating, getting staff"""
    
    @token_auth.login_required(role=['sys_admin', 'staff_admin'])
    @responds(schema=StaffSchema(many=True), api=ns)
    def get(self):
        """returns all staff members"""
        #TODO add search functionality
        all_staff = Staff.query.all()

        return all_staff    
    
    @token_auth.login_required(role=['sys_admin', 'staff_admin'])
    @accepts(schema=StaffSchema, api=ns)
    @responds(schema=StaffSchema, status_code=201, api=ns)     
    def post(self):
        """register a new staff member"""
        data = request.get_json() or {}
        #check if this email is already being used
        staff = Staff.query.filter_by(email=data.get('email')).first()
        if staff:
            raise StaffEmailInUse(email=data.get('email'))

        # allow only system admin to add staff admin roles. staff admin can create all other roles except staff/systemadmin
        if data.get('is_system_admin'):
            raise UnauthorizedUser(message=f"Staff member with email {token_auth.current_user().email} is unauthorized to create a system administrator role.")

        if data.get('is_admin') and token_auth.current_user().get_admin_role() != 'sys_admin':
            raise UnauthorizedUser(message=f"Staff member with email {token_auth.current_user().email} is unauthorized to create a staff administrator role. \
                                 Please contact system admin")
   
        staff_schema = StaffSchema()

        new_staff = staff_schema.load(data)

        db.session.add(new_staff)
        db.session.commit()

        return new_staff

    