from flask import request, jsonify
from flask_restx import Resource, fields
from flask_accepts import accepts , responds

from odyssey import db
from odyssey.models.staff import Staff
from odyssey.api import api
from odyssey.api.auth import token_auth
from odyssey.api.errors import UnauthorizedUser, StaffEmailInUse, StaffNotFound
from odyssey.utils.schemas import StaffSchema, StaffSearchItemsSchema

ns = api.namespace('staff', description='Operations related to staff members')

@ns.route('/')
@ns.doc(params={'firstname': 'first name to search',
                'lastname': 'last name to search',
                'staffid': 'staffid to search',
                'email': 'email to search'})
class StaffMembers(Resource):
    """staff member class for creating, getting staff"""
    
    @token_auth.login_required(role=['sys_admin', 'staff_admin'])
    @responds(schema=StaffSearchItemsSchema(many=True), api=ns)
    def get(self):
        """returns list of staff members given query parameters"""                
        # These payload keys should be the same as what's indexed in 
        # the model.
        param = {}
        param_keys = ['firstname', 'lastname', 'email', 'staffid']
        noMoreSearch = False
        if not request.args:
            data = Staff.query.order_by(Staff.lastname.asc()).all()
            noMoreSearch = True
        
        if not noMoreSearch:
            searchStr = ''
            count = 0
            onlyStaffID = False
            exactMatch = False
            for key in param_keys:
                param[key] = request.args.get(key, default=None, type=str)
                # Cleans up search query
                if param[key] is None:
                    param[key] = ''
                    # This checks if staffid is the only searching criteria
                    if key != 'staffid':
                        count+=1        
                elif key == 'email' and param.get(key, None):
                    tempEmail = param[key]
                    param[key] = param[key].replace("@"," ")
                searchStr = searchStr + param[key] + ' '
            
            if count == len(param_keys)-1:
                onlyStaffID = True

            if onlyStaffID:
                data = [Staff.query.filter_by(staffid=param['staffid']).first()]
                if not any(data):
                    raise StaffNotFound(param['staffid'])
                exactMatch = True
            else:
                data = Staff.query.whooshee_search(searchStr).all()

            # Since email and staffid should be unique, 
            # if the input email or staffid exactly matches 
            # the profile, only display that user
            if param['email']:
                for val in data:
                    if val.email.lower() == tempEmail.lower():
                        data = [val]
                        exactMatch = True
                        break

            # Assuming staff will most likely remember their 
            # email instead of their staff. If the email is correct
            # no need to search through RLI. 
            #
            # This next check depends on if the whooshee search returns 
            # Relevant staff with the correct ID. It is possible for the
            # search to return different staff members (and NOT the staffid
            # that was a search parameter
            #
            # If BOTH are incorrect, return data as normal.
            if param['staffid'] and not exactMatch:
                for val in data:
                    if val.staffid == param['staffid']:
                        data = [val]
                        break
        return data 
    
    @token_auth.login_required(role=['sys_admin', 'staff_admin'])
    @accepts(schema=StaffSchema, api=ns)
    @responds(schema=StaffSchema, status_code=201, api=ns)     
    def post(self):
        """register a new staff member"""
        data = request.get_json() or {}
        #check if this email is already being used. If so raise 409 conflict error 
        staff = Staff.query.filter_by(email=data.get('email')).first()
        if staff:
            raise StaffEmailInUse(email=data.get('email'))

        ## Role suppression
        # system_admin: permisison to create staff admin.
        # staff_admin:  can create all other roles except staff/systemadmin
        if data.get('is_system_admin'):
            raise UnauthorizedUser(message=f"Staff member with email {token_auth.current_user().email} is unauthorized to create a system administrator role.")

        if data.get('is_admin') and token_auth.current_user().get_admin_role() != 'sys_admin':
            raise UnauthorizedUser(message=f"Staff member with email {token_auth.current_user().email} is unauthorized to create a staff administrator role. \
                                 Please contact system admin")
   
        # Staff schema instance load from payload
        staff_schema = StaffSchema()

        new_staff = staff_schema.load(data)

        db.session.add(new_staff)
        db.session.commit()

        return new_staff

    