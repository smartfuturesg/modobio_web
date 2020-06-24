
from hashlib import md5

from flask import jsonify, request
from flask_restx import Resource

from odyssey import db
from odyssey.api import api
from odyssey.api.auth import basic_auth, basic_auth_client
from odyssey.api.auth import token_auth
from odyssey.api.clients import ns as client_ns
from odyssey.api.errors import UserNotFound
from odyssey.models.intake import RemoteRegistration
# from odyssey.api.serializers import remote_registration


ns = api.namespace('tokens', description='Operations related to token authorization')
ns = api.namespace('tokens', description='Operations related to token authorization')

@ns.route('/')
class Token(Resource):
    """create and revoke tokens"""
    @ns.doc(security='basic')
    @basic_auth.login_required
    def post(self):
        """generates a token for the 'current_user' immediately after password authentication"""
        user = basic_auth.current_user()
        return {'email': user.email, 
                'firstname': user.firstname, 
                'lastname': user.lastname, 
                'token': user.get_token(),
                'access_role': user.access_role}, 201

    @ns.doc(security='basic')
    @token_auth.login_required
    def delete(self):
        """invalidate urrent token. Used to effectively logout a user"""
        token_auth.current_user().revoke_token()
        return '', 204

@ns.route('/remoteregistration/<string:tmp_registration>/')
class RemoteRegistrationToken(Resource):
    @ns.doc(security='basic')
    @basic_auth_client.login_required
    def post(self, tmp_registration):
        #check if temporary registration endpoint is valid
        user = basic_auth_client.current_user()
        if tmp_registration != md5(bytes((user.email), 'utf-8')).hexdigest():
            raise UserNotFound(clientid=0, message = f"The client with email: {user.email} does not yet exist") 
        return {'email': user.email, 'token': user.get_token()}, 201
