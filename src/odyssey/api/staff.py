from flask import request

from odyssey import db
from odyssey.models.main import Staff
from odyssey.api import bp
from odyssey.api.auth import token_auth
from odyssey.api.errors import bad_request

@bp.route('/staff/register', methods=['POST'])
@token_auth.login_required
def register_new_staff():
    """register a new staff member"""
    data = request.get_json() or {}
    #TODO make sure only admin accounts can register new staff

    if 'firstname' not in data or 'lastname' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include name, email and password fields')
    if Staff.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email')

    new_staff = Staff()
    new_staff.from_dict(data, new_staff=True)

    db.session.add(new_staff)
    db.session.commit()
    response = new_staff.to_dict()
    return response, 201