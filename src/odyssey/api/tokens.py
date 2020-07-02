
from hashlib import md5

from flask import jsonify, request
from flask_restx import Resource

from odyssey import db
from odyssey.api import api
from odyssey.api.auth import basic_auth, basic_auth_client
from odyssey.api.auth import token_auth, token_auth_client
from odyssey.api.clients import ns as client_ns
from odyssey.api.errors import UserNotFound, ClientNotFound
from odyssey.models.intake import RemoteRegistration
# from odyssey.api.serializers import remote_registration


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
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class RemoteRegistrationToken(Resource):
    """generate and delete portal user API access tokens
        first validates that the user's basic authentication passes, then checks
        the url to validate the authenticity of the end point (i.e. in database and not expired)"""
    @ns.doc(security='basic')
    @basic_auth_client.login_required
    def post(self, tmp_registration):
        """generate api token for portal user"""
        #validate registration portal
        if not RemoteRegistration().check_portal_id(tmp_registration):
            raise ClientNotFound(message="Resource does not exist")
        
        user = basic_auth_client.current_user()

        return {'email': user.email, 'token': user.get_token()}, 201

    @ns.doc(security='basic')
    @basic_auth_client.login_required
    def delete(self, tmp_registration):
        """invalidate current token. Used to effectively logout a user"""
        token_auth_client.current_user().revoke_token()
        return '', 204
