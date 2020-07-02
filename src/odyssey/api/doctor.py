from flask import request

from odyssey.models.doctor import MedicalPhysicalExam, MedicalHistory
from odyssey.api import bp
from odyssey.api.auth import token_auth

@bp.route('/doctor/medicalhistory/<int:clientid>/', methods=['GET'])
#@token_auth.login_required
def get_medical_history(clientid):
    """returns medical history for the specified client id"""
    return MedicalHistory.query.filter_by(clientid=clientid).first_or_404().to_dict()

@bp.route('/doctor/medicalphysicalexam/<int:clientid>/', methods=['GET'])
@token_auth.login_required
def get_medical_physical(clientid):
    """returns medical history for the specified client id"""
    return MedicalPhysicalExam.query.filter_by(clientid=clientid).first_or_404().to_dict()

