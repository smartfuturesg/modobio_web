from datetime import datetime, timedelta
import secrets
import jwt

from flask import current_app, request, url_for, jsonify
from flask_accepts import accepts, responds
from flask_restx import Resource
from werkzeug.security import check_password_hash


from odyssey.api import api
from odyssey.utils.errors import ContentNotFound, InputError, StaffEmailInUse, ClientEmailInUse, UnauthorizedUser
from odyssey.utils.email import send_email_password_reset, send_email_delete_account
from odyssey.api.user.schemas import (
    UserSchema, 
    UserLoginSchema,
    UserPasswordRecoveryContactSchema,
    UserPasswordResetSchema,
    UserPasswordUpdateSchema,
    NewUserSchema,
    UserInfoSchema
) 
from odyssey.api.staff.schemas import StaffProfileSchema, StaffRolesSchema
from odyssey.api.client.schemas import ClientInfoSchema
from odyssey.api.user.models import User, UserLogin, UserRemovalRequests
from odyssey.utils.misc import check_user_existence
from odyssey.utils.auth import token_auth

from odyssey import db

ns = api.namespace('user', description='Endpoints for user accounts.')

@ns.route('/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ApiUser(Resource):
    
    @token_auth.login_required
    @responds(schema=UserSchema, api=ns)
    def get(self, user_id):
        check_user_existence(user_id)

        return User.query.filter_by(user_id=user_id).one_or_none()

    @token_auth.login_required()
    def delete(self, user_id):
        #Search for user by user_id in User table
        check_user_existence(user_id)
        user = User.query.filter_by(user_id=user_id).one_or_none()
        requester = token_auth.current_user()[0]
        removal_request = UserRemovalRequests(
            requester_user_id=requester.user_id, 
            deleting_user_id=user.user_id)

        db.session.add(removal_request)
        db.session.flush()

        
        if user.is_staff and user.is_client:
            print("is both")
        
        elif user.is_staff:
            print("it's staff only")
        
        else:
            user.email = ""
            user.phone_number = ""
            user.firstname = ""
            user.middlename = ""
            user.lastname = ""
            

        #logic to email user being deleted and user requesting deletion
        if user.email != requester.email:
            send_email_delete_account(requester.email, user.email)
        send_email_delete_account(user.email, user.email)

        #db.session.delete(user)
        db.session.commit()

        return {'message': f'User with id {user_id} has been removed'}

@ns.route('/staff/')
class NewStaffUser(Resource):
    @token_auth.login_required
    @accepts(schema=NewUserSchema, api=ns)
    @responds(schema=UserSchema, status_code=201, api=ns)
    def post(self):
        """
        Create a staff user. Payload will require userinfo and staffinfo
        sections. Currently, staffinfo is used to register the staff user with 
        one or more access_roles. This endpoint expects a password field. 
        """
        data = request.get_json()
        
        # Check if user exists already
        user_info = data.get('userinfo')
        staff_info = data.get('staffinfo')

        user = User.query.filter(User.email.ilike(user_info.get('email'))).first()
        if user:
            if user.is_staff:
                # user account already exists for this email and is already a staff account
                raise StaffEmailInUse(email=user_info.get('email'))
            else:
                #user account exists but only the client portion of the account is defined
                user.is_staff = True
                staff_profile = StaffProfileSchema().load({'user_id': user.user_id})
                db.session.add(staff_profile)
        else:
            # user account does not yet exist for this email
            # require password
            password = user_info.get('password', None)
            if not password:
                raise InputError(status_code=400,message='password required')
            del user_info['password']
            
            user_info["is_client"] = False
            user_info["is_staff"] = True
            # create entry into User table first
            # use the generated user_id for UserLogin & StaffProfile tables
            user = UserSchema().load(user_info)
            db.session.add(user) 
            db.session.flush()

            user_login = UserLoginSchema().load({"user_id": user.user_id, "password": password})
            staff_profile = StaffProfileSchema().load({"user_id": user.user_id})
            db.session.add(user_login)
            db.session.add(staff_profile)
            
        # create entries for role assignments 
        for role in staff_info.get('access_roles', []):
            db.session.add(StaffRolesSchema().load(
                                            {'user_id': user.user_id,
                                             'role': role}
                                            ))
        db.session.commit()
        return user

@ns.route('/client/')
class NewClientUser(Resource):
    @accepts(schema=NewUserSchema, api=ns)
    @responds(schema=UserInfoSchema, status_code=201, api=ns)
    def post(self): 
        """
        Create a client user. This endpoint requires a payload with just
        userinfo. Passwords are auto-generated by the API and 
        returned in the payload. 
        """
        data = request.get_json()     

        user_info = data.get('userinfo')
        user = User.query.filter(User.email.ilike(user_info.get('email'))).first()
        if user:
            if user.is_client:
                # user account already exists for this email and is already a client account
                raise ClientEmailInUse(email=user_info.get('email'))
            else:
                # user account exists but only the staff portion of the account is defined
                user.is_client = True
                client_info = ClientInfoSchema().load({'user_id': user.user_id})
                password=""
                db.session.add(client_info)
        else:
            # user account does not yet exist for this email
            # create a password
            password=user_info.get('password')
            if not password:
                password = user_info.get('email')[:2]+secrets.token_hex(4)
            else:
                del user_info['password']
            user_info["is_client"] = True
            user_info["is_staff"] = False
            user = UserSchema().load(user_info)
            db.session.add(user)
            db.session.flush()
            user_login = UserLoginSchema().load({"user_id": user.user_id, "password": password})
            client_info = ClientInfoSchema().load({"user_id": user.user_id})
            db.session.add(client_info)
            db.session.add(user_login)

        payload=user.__dict__
        payload['password']=password
        
        db.session.commit()

        return user

@ns.route('/password/forgot-password/recovery-link/')
class PasswordResetEmail(Resource):
    """Password reset endpoints."""
    
    @accepts(schema=UserPasswordRecoveryContactSchema, api=ns)
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
        email = request.parsed_obj['email']

        user = User.query.filter_by(email=email.lower()).first()
        
        if not email or not user:
            return 200

        secret = current_app.config['SECRET_KEY']
        encoded_token = jwt.encode({'exp': datetime.utcnow()+timedelta(minutes = 15), 
                                  'sid': user.user_id}, 
                                  secret, 
                                  algorithm='HS256').decode("utf-8") 
        if current_app.env == "development":
            return jsonify({"token": encoded_token})
        else:
            send_email_password_reset(user.email, encoded_token)
            return 200
        

@ns.route('/password/forgot-password/reset')
@ns.doc(params={'reset_token': "token from password reset endpoint"})
class ResetPassword(Resource):
    """Reset the user's password."""

    @accepts(schema=UserPasswordResetSchema, api=ns)
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
        pswd = request.parsed_obj['password']

        user = UserLogin.query.filter_by(user_id=decoded_token['sid']).first()
        user.set_password(pswd)

        db.session.commit()

        return 200

@ns.route('/password/update/')
class ChangePassword(Resource):
    """Reset the user's password."""
    @token_auth.login_required
    @accepts(schema=UserPasswordUpdateSchema, api=ns)
    def post(self):
        """
            Change the current password to the one given
            in the body of this request
            response 200 OK
        """
        # bring up the staff member and reset their password
        _, user_login = token_auth.current_user()

        if check_password_hash(user_login.password, request.parsed_obj['current_password']):
            user_login.set_password(request.parsed_obj['new_password'])
        else:
            raise UnauthorizedUser(message="please enter the correct current password \
                                      otherwise, visit the password recovery endpoint \
                                      /staff/password/forgot-password/recovery-link")
        db.session.commit()

        return 200

@ns.route('/token/refresh')
@ns.doc(params={'refresh_token': "token from password reset endpoint"})
class RefreshToken(Resource):
    """User refesh token to issue a new token with a 1 hr TTL"""
    def post(self):
        """
        Issues new API access token if refrsh_token is still valid
        """
        refresh_token = request.args.get("refresh_token")
        secret = current_app.config['SECRET_KEY']
        
        # check that the token is valid
        try:
            decoded_token = jwt.decode(refresh_token, secret, algorithms='HS256')
        except jwt.ExpiredSignatureError:
            raise UnauthorizedUser(message="")
        
        # if valid, create a new access token, return it in the payload
        token = UserLogin.generate_token(user_id=decoded_token['uid'], user_type=decoded_token['utype'], token_type='access')    
        
        return {'access_token': token}, 201