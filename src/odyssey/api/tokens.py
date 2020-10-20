from hashlib import md5

from flask import request, jsonify, current_app
from flask_restx import Resource

from odyssey import db
from odyssey.api import api
from odyssey.api.auth import basic_auth, basic_auth_client
from odyssey.api.auth import token_auth, token_auth_client
from odyssey.api.clients import ns as client_ns
from odyssey.api.errors import UserNotFound, ClientNotFound
from odyssey.models.client import RemoteRegistration


ns = api.namespace('tokens', description='Operations related to token authorization')

@ns.route('/staff/')
class Token(Resource):
    """create and revoke tokens"""
    @ns.doc(security='password')
    @basic_auth.login_required
    def post(self):
        """generates a token for the 'current_user' immediately after password authentication"""
        user = basic_auth.current_user()
        return {'email': user.email, 
                'firstname': user.firstname, 
                'lastname': user.lastname, 
                'token': user.get_token(),
                'access_roles': user.access_roles}, 201

    @ns.doc(security='password')
    @token_auth.login_required
    def delete(self):
        """invalidate urrent token. Used to effectively logout a user"""
        token_auth.current_user().revoke_token()
        return '', 204

@ns.route('/remoteregistration/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class RemoteRegistrationToken(Resource):
    """generate and delete portal user API access tokens
        first validates that the user's basic authentication passes, then checks
        the url to validate the authenticity of the end point (i.e. in database and not expired)"""
    
    @ns.doc(security='password')
    @basic_auth_client.login_required
    def post(self):
        """generate api token for portal user"""
        tmp_registration = request.args.get('tmp_registration')
        #validate registration portal
        if not RemoteRegistration().check_portal_id(tmp_registration):
            raise ClientNotFound(message="Resource does not exist")
        user = basic_auth_client.current_user()

        return {'email': user.email, 'token': user.get_token()}, 201

    @ns.doc(security='password')
    @basic_auth_client.login_required
    def delete(self):
        """invalidate current token. Used to effectively logout a user"""
        token_auth_client.current_user().revoke_token()
        return '', 204
