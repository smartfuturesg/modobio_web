from flask import request

from odyssey.models.doctor import MedicalPhysicalExam, MedicalHistory
from odyssey.api import bp
from odyssey.api.auth import token_auth

@bp.route('/doctor/medicalhistory/<int:client_id>', methods=['GET'])
def get_medical_history(client_id):
    """returns medical history for the specified client id"""
    return MedicalHistory.query.filter_by(clientid=client_id).first_or_404().to_dict()

@bp.route('/doctor/medicalphysicalexam/<int:client_id>', methods=['GET'])
def get_medical_physical(client_id):
    """returns medical history for the specified client id"""
    return MedicalPhysicalExam.query.filter_by(clientid=client_id).first_or_404().to_dict()