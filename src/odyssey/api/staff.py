from datetime import datetime, timedelta
import secrets

from flask import current_app, request, jsonify
from flask_restx import Resource, fields
from flask_accepts import accepts, responds
import jwt

from odyssey import db
from odyssey.models.staff import Staff
from odyssey.api import api
from odyssey.api.auth import token_auth, basic_auth
from odyssey.api.errors import UnauthorizedUser, StaffEmailInUse, StaffNotFound
from odyssey.utils.email import send_email_password_reset
from odyssey.utils.schemas import (
    StaffPasswordRecoveryContactSchema, 
    StaffPasswordResetSchema,
    StaffPasswordUpdateSchema,
    StaffSchema, 
    StaffSearchItemsSchema
)

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
        elif len(request.args) == 1 and request.args.get('staffid'):
            data = [Staff.query.filter_by(staffid=request.args.get('staffid')).first()]
            if not any(data):
                raise StaffNotFound(request.args.get('staffid'))
            noMoreSearch = True
        
        if not noMoreSearch:
            searchStr = ''
            exactMatch = False
            for key in param_keys:
                param[key] = request.args.get(key, default=None, type=str)
                # Cleans up search query
                if param[key] is None:
                    param[key] = ''     
                elif key == 'email' and param.get(key, None):
                    tempEmail = param[key]
                    param[key] = param[key].replace("@"," ")
                searchStr = searchStr + param[key] + ' '
            
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

@ns.route('/password/forgot-password/recovery-link')
class PasswordResetEmail(Resource):
    """Password reset endpoints."""
    
    @accepts(schema=StaffPasswordRecoveryContactSchema, api=ns)
    def post(self):
        """begin a password reset session. 
            Staff member unable to log in will request a password reset
            with only their email. Emails will be checked for exact match in the database
            to a staff member. 
    
            If the email exists, a signed JWT is created; encoding the token's expiration 
            time and the staffid. The code will be placed into this URL <url for password reset>
            and sent to a valid email address.  
            If the email does not exist, no email is sent. 
            response 200 OK
        """
        email = request.get_json()['email']

        staff = Staff.query.filter_by(email=email.lower()).first()
        
        if not email or not staff:
            return 200

        secret = current_app.config['SECRET_KEY']
        encoded_token = jwt.encode({'exp': datetime.utcnow()+timedelta(minutes = 1), 
                                  'sid': staff.staffid}, 
                                  secret, 
                                  algorithm='HS256').decode("utf-8") 

        send_email_password_reset(staff.email, encoded_token)
        
        if current_app.env == "development":
            return jsonify({"token": encoded_token})
        else:
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
            return UnauthorizedUser(message="Token authorization expired")

        # bring up the staff member and reset their password
        pswd = request.get_json()['password']

        staff = Staff.query.filter_by(staffid=decoded_token['sid']).first()
        staff.set_password(pswd)

        db.session.commit()

        return 200

@ns.route('password/update')
class ChangePassword(Resource):
    """Reset the user's password."""
    @token_auth.login_required()
    @accepts(schema=StaffPasswordUpdateSchema, api=ns)
    def put(self):
        """
            Change the current password to the one given
            in the body of this request
            response 200 OK
       """
        data = request.get_json()
        staff_email = token_auth.current_user().email

        # bring up the staff member and reset their password
        pswd = request.get_json()['password']

        staff = Staff.query.filter_by(email=staff_email).first()
        if staff.check_password(password=data["current_password"]):
            staff.set_password(data["new_password"]):
        else:
            UnauthorizedUser(message="please enter the correct current password \
                                      otherwise, visit the password recovery endpoint \
                                      /staff/password/forgot-password/recovery-link")

        db.session.commit()

        return 200



