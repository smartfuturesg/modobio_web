
from flask import jsonify, request
from flask_restx import Resource
from odyssey import db
from odyssey.api import api
from odyssey.api.auth import basic_auth
from odyssey.api.auth import token_auth

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

