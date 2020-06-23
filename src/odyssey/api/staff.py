from flask import request
from flask_restx import Resource, fields

from odyssey import db
from odyssey.models.main import Staff
from odyssey.api import api
from odyssey.api.auth import token_auth
from odyssey.api.errors import UnauthorizedUser
from odyssey.api.serializers import new_staff_member

ns = api.namespace('staff', description='Operations related to staff members')


@ns.route('/')
class StaffMembers(Resource):
    """staff member class for creating, getting, altering staff"""
    @ns.expect(new_staff_member, validate=True)
    @token_auth.login_required(role=['sys_admin', 'staff_admin'])
    def post(self):
        """register a new staff member"""
        data = request.get_json() or {}
  
        if data['is_system_admin']:
            raise UnauthorizedUser(message=f"Staff member with email {token_auth.current_user().email} is unauthorized to create a system administrator role.")

        if data['is_admin'] and token_auth.current_user().get_admin_role() != 'sys_admin':
            raise UnauthorizedUser(message=f"Staff member with email {token_auth.current_user().email} is unauthorized to create a staff administrator role. \
                                 Please contact system admin")
   
        new_staff = Staff()
        new_staff.from_dict(data, new_staff=True)

        db.session.add(new_staff)
        db.session.flush()
        db.session.commit()
        response = new_staff.to_dict()
        return response, 201