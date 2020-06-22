from flask import request

from odyssey.models.doctor import MedicalPhysicalExam, MedicalHistory
from odyssey.api import bp
from odyssey.api.auth import token_auth

@bp.route('/pt/history/<int:clientid>/', methods=['GET'])
#@token_auth.login_required
def get_pt_history(clientid):
    """returns medical history for the specified client id"""
    return {'response': 'nothing here yet'}

@bp.route('/pt/mobility/<int:clientid>/', methods=['GET'])
@token_auth.login_required
def get_mobility_assessment(clientid):
    """returns medical history for the specified client id"""
    return {'response': 'nothing here yet'}

