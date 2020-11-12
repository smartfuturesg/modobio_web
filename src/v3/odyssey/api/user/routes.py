from flask import request
from flask_accepts import accepts, responds
from flask_restx import Resource

from odyssey.api import api
from odyssey.utils.errors import StaffEmailInUse, ClientEmailInUse
from odyssey.api.user.schemas import UserSchema, UserLoginSchema, NewUserSchema
from odyssey.api.staff.schemas import StaffProfileSchema
from odyssey.api.client.schemas import ClientInfoSchema
from odyssey.api.user.models import User
from odyssey.utils.misc import check_user_existence
from odyssey.utils.auth import token_auth

from odyssey import db

ns = api.namespace('user', description='Endpoints for user accounts.')

@ns.route('/<int:user_id>/')
class ApiUser(Resource):
    
    @token_auth.login_required
    @responds(schema=UserSchema, api=ns)
    def get(self, user_id):
        check_user_existence(user_id)

        return User.query.filter_by(user_id=user_id).one_or_none()


@ns.route('/')
class ApiNewUser(Resource):
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
            else:
                #user account does not yet exist for this email
                password = data['password']
                del data['password']
                user = UserSchema().load(data)
                db.session.add(user)
                db.session.flush()
                user_login = UserLoginSchema().load({"user_id": user.user_id, "password": password})
                staff_profile = StaffProfileSchema().load({"user_id": user.user_id})
                db.session.add(user_login)
                db.session.add(staff_profile)
        else:
            user = User.query.filter_by(email=data.get('email')).first()
            if user:
                if user.is_client:
                    #user account already exists for this email and is already a client account
                    raise ClientEmailInUse(email=data.get('email'))
                else:
                    #user account exists but only the staff portion of the account is defined
                    user.is_client = True
                    client_info = ClientInfoSchema().load({'user_id': user.user_id})
                    db.session.add(client_info)
            else:
                #user account does not yet exist for this email
                password = data['password']
                del data['password']
                user = UserSchema().load(data)
                db.session.add(user)
                db.session.flush()
                user_login = UserLoginSchema().load({"user_id": user.user_id, "password": password})
                client_info = ClientInfoSchema().load({"user_id": user.user_id})
                db.session.add(client_info)
                db.session.add(user_login)
        db.session.commit()

        return user