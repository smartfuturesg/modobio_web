
from flask import jsonify
from odyssey import db
from odyssey.api import bp
from odyssey.api.auth import basic_auth
from odyssey.api.auth import token_auth

@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    """generates a token for the 'current_user' immediately after password authentication"""
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return {'token': token}


@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204