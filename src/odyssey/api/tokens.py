
from flask import jsonify
from flask_restx import Resource
from odyssey import db
from odyssey.api import api
from odyssey.api.auth import basic_auth
from odyssey.api.auth import token_auth

@api.route('/tokens')
class Token(Resource):
    """create and revoke tokens"""
    @basic_auth.login_required
    def post(self):
        """generates a token for the 'current_user' immediately after password authentication"""
        token = basic_auth.current_user().get_token()
        db.session.commit()
        return {'token': token}

    @token_auth.login_required
    def delete(self):
        token_auth.current_user().revoke_token()
        db.session.commit()
        return '', 204

