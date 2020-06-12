from flask import request

from odyssey.models.doctor import MedicalPhysicalExam, MedicalHistory
from odyssey.api import bp
from odyssey.api.auth import token_auth

@bp.route('/pt/history/<int:client_id>', methods=['GET'])
#@token_auth.login_required
def get_pt_history(client_id):
    """returns medical history for the specified client id"""
    return {'response': 'nothing here yet'}

@bp.route('/pt/mobility/<int:client_id>', methods=['GET'])
@token_auth.login_required
def get_mobility_assessment(client_id):
    """returns medical history for the specified client id"""
    return {'response': 'nothing here yet'}

