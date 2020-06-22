
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
        token = basic_auth.current_user().get_token()
        #db.session.commit()
        return {'token': token}

    @ns.doc(security='basic')
    @token_auth.login_required
    def delete(self):
        token_auth.current_user().revoke_token()
        db.session.commit()
        return '', 204

