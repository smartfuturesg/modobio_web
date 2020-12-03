from datetime import datetime, timedelta
import secrets
import jwt

from flask import current_app, request, url_for, jsonify
from flask_accepts import accepts, responds
from flask_restx import Resource

from odyssey import db
from odyssey.api import api
from odyssey.api.client_services.schemas import NewUserSchema, NewUserRegistrationPortalSchema
from odyssey.api.user.schemas import UserLoginSchema, UserSchema
from odyssey.api.user.models import User, UserLogin
from odyssey.utils.auth import token_auth
from odyssey.utils.constants import REGISTRATION_PORTAL_URL
from odyssey.utils.email import send_email_user_registration_portal
from odyssey.utils.errors import ClientEmailInUse, InputError


ns = api.namespace('client-services', description='Endpoints for client services operations.')

@ns.route('/user/new/')
class NewUserClientServices(Resource):
    """
    Create, Update, Retrieve user basic information. 
    This endpoint is intended to be used by client services. 
    """

    @token_auth.login_required(user_type=('staff', ), staff_role=('client_services',
                                                                  'client_services_internal'))
    @accepts(schema=NewUserSchema, api=ns)
    @responds(schema=NewUserRegistrationPortalSchema, api=ns, status_code=201)
    def post(self):
        """
        Create new user using only email (and/or phone number) and name. Returns a password and portal link for the new user.
        Portal link includes a portal_id which is a JWT with a 24 hour lifetime. Clients must use this link
        """
        data = request.parsed_obj
        user_type = data.get('user_type')
        del data['user_type']
        user = User.query.filter(User.email.ilike(data.get('email').lower())).first()
        if user:
            raise ClientEmailInUse(email=(data.get('email')))
        password = data.get('email')[:2] + secrets.token_hex(8)
        data['is_client'] = False
        data['is_staff'] = False
        user = UserSchema().load(data)
        db.session.add(user)
        db.session.flush()

        user_login = UserLoginSchema().load({'user_id':user.user_id,  'password':password})
        db.session.add(user_login)
        # db.session.commit()

        secret = current_app.config['SECRET_KEY']
        portal_id = jwt.encode({'exp':datetime.utcnow() + timedelta(hours=24),  
                                'utype':data.get('user_type')},
                                secret,
                                algorithm='HS256').decode('utf-8')

        send_email_user_registration_portal(user.email, password, portal_id)

        return {'password':password,
                'registration_portal_url': REGISTRATION_PORTAL_URL.format(portal_id)}
