from datetime import datetime, timedelta

from flask import current_app, request, url_for
from flask_accepts import accepts, responds
from flask_restx import Resource
from requests_oauthlib import OAuth2Session

from odyssey.api import api
from odyssey.api.auth import token_auth
from odyssey.api.errors import ContentNotFound, StaffEmailInUse, ClientEmailInUse

from odyssey import db

ns = api.namespace('users', description='Endpoints for user accounts.')

@ns.route('/')
class User(Resource):
    
    @token_auth.login_required
    @responds(schema=UserSchema, api=ns)
    def get(self):
        check_user_existence(user_id)

        return User.query.filter_by(user_id=user_id).one_or_none()


@ns.route('/<int:user_id>/')
class NewUser(Resource):

    @token_auth.login_required
    @accepts(schema=NewUserSchema, api=ns)
    @responds(schema=UserSchema, status_code=201, api=ns)
    def post(self):
        
        data = request.get_json()

        #staff user account creation request
        if data['is_staff']:
            user = User.query.filter_by(email=data.get('email')).first()
            if user:
                if user.is_staff:
                    #user account already exists for this email and is already a staff account
                    raise StaffEmailInUse(email=data.get('email'))
                else:
                    #user account exists but only the client portion of the account is defined
                    user.is_staff = True
                    staff_profile = StaffProfileSchema().load({'user_id': user.user_id})
                    db.session.add(staff_profile)
                    db.session.commit()
            else:
                #user account does not yet exist for this email
        else:
            user = User.query.filter_by(email=data.get('email')).first()
            if user:
                if user.is_client:
                    #user account already exists for this email and is already a client account
                    raise ClientEmailInUse(email=data.get('email'))
                else:
                    #user account exists but only the staff portion of the account is defined

            else:
                #user account does not yet exist fo this email
        