import logging
logger = logging.getLogger(__name__)

from flask import request
from flask_restx import Namespace
from flask_accepts import accepts, responds

from odyssey import db
from odyssey.api.doctor.models import MedicalPhysicalExam
from odyssey.api.trainer.models import (
    FitnessQuestionnaire,
    HeartAssessment,
    LungAssessment,
    MovementAssessment,
    MoxyAssessment,
    MoxyRipTest,
    PowerAssessment,
    StrengthAssessment 
)
from odyssey.api.trainer.schemas import (
    FitnessQuestionnaireSchema,
    HeartAssessmentSchema,
    LungAssessmentSchema,
    MovementAssessmentSchema,
    MoxyAssessmentSchema,
    MoxyRipSchema,
    PowerAssessmentSchema, 
    StrenghtAssessmentSchema
)
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource
from odyssey.utils.misc import check_client_existence

ns = Namespace('trainer', description='Operations related to the trainer')

@ns.route('/assessment/power/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class Power(BaseResource):
    """GET and POST power assessments for the client"""
    @token_auth.login_required
    @responds(schema=PowerAssessmentSchema(many=True), api=ns)
    def get(self, user_id):
        """returns all power assessment entries for the specified client"""
        check_client_existence(user_id)

        all_entries = PowerAssessment.query.filter_by(user_id=user_id).order_by(PowerAssessment.timestamp.asc()).all()

        if len(all_entries) == 0:
            recent_physical = MedicalPhysicalExam.query.filter_by(user_id=user_id).order_by(MedicalPhysicalExam.idx.desc()).first()
            if not recent_physical:
                vital_weight = None
            else:
                vital_weight = recent_physical.vital_weight
            data_dict = {
                'vital_weight': vital_weight,
                'user_id': user_id}
            # raise ContentNotFoundReturnData(user_id=user_id, data=data_dict)
            return data_dict

        return all_entries

    @token_auth.login_required
    @accepts(schema=PowerAssessmentSchema, api=ns)
    @responds(schema=PowerAssessmentSchema, status_code=201, api=ns)
    def post(self, user_id):
        """create a power assessment entry for user_id"""
        check_client_existence(user_id)

        data=request.get_json()
        data['user_id'] = user_id
        
        pa_schema = PowerAssessmentSchema()
        client_pa = pa_schema.load(data)

        db.session.add(client_pa)
        db.session.commit()

        most_recent =  PowerAssessment.query.filter_by(user_id=user_id).order_by(PowerAssessment.timestamp.desc()).first()
        return most_recent

@ns.route('/assessment/strength/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class Strength(BaseResource):
    """GET and POST strength assessments for the client"""
    @token_auth.login_required
    @responds(schema=StrenghtAssessmentSchema(many=True), api=ns)
    def get(self, user_id):
        """returns all strength assessment entries for the specified client"""
        check_client_existence(user_id)

        all_entries = StrengthAssessment.query.filter_by(user_id=user_id).order_by(StrengthAssessment.timestamp.asc()).all()
        
        return all_entries

    @token_auth.login_required
    @accepts(schema=StrenghtAssessmentSchema, api=ns)
    @responds(schema=StrenghtAssessmentSchema, status_code=201, api=ns)
    def post(self, user_id):
        """create a strength assessment entry for user_id"""
        check_client_existence(user_id)

        data=request.get_json()
        data['user_id'] = user_id

        sa_schema = StrenghtAssessmentSchema()
        client_sa = sa_schema.load(data)

        db.session.add(client_sa)
        db.session.commit()
        
        most_recent = StrengthAssessment.query.filter_by(user_id=user_id).order_by(StrengthAssessment.timestamp.desc()).first()
        return most_recent


@ns.route('/assessment/movement/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class Movement(BaseResource):
    """GET and POST movement assessments for the client"""
    @token_auth.login_required
    @responds(schema=MovementAssessmentSchema(many=True), api=ns)
    def get(self, user_id):
        """returns all movement assessment entries for the specified client"""
        check_client_existence(user_id)

        all_entries = MovementAssessment.query.filter_by(user_id=user_id).order_by(MovementAssessment.timestamp.asc()).all()
        
        return all_entries

    @token_auth.login_required
    @accepts(schema=MovementAssessmentSchema, api=ns)
    @responds(schema=MovementAssessmentSchema, status_code=201, api=ns)
    def post(self, user_id):
        """create a movement assessment entry for user_id"""
        check_client_existence(user_id)

        data=request.get_json()
        data['user_id'] = user_id

        sa_schema = MovementAssessmentSchema()
        client_sa = sa_schema.load(data)

        db.session.add(client_sa)
        db.session.commit()
        
        most_recent = MovementAssessment.query.filter_by(user_id=user_id).order_by(MovementAssessment.timestamp.desc()).first()
        return most_recent

@ns.route('/assessment/heart/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class Heart(BaseResource):
    """GET and POST movement assessments for the client"""

    @token_auth.login_required
    @responds(schema=HeartAssessmentSchema(many=True), api=ns)
    def get(self, user_id):
        """returns all cardio assessment entries for the specified client"""
        check_client_existence(user_id)

        all_entries = HeartAssessment.query.filter_by(user_id=user_id).order_by(HeartAssessment.timestamp.asc()).all()

        if len(all_entries) == 0:
            recent_physical = MedicalPhysicalExam.query.filter_by(user_id=user_id).order_by(MedicalPhysicalExam.idx.desc()).first()
            if not recent_physical:
                vital_heartrate = None
            else:
                vital_heartrate = recent_physical.vital_heartrate
            data_dict = {
                'vital_heartrate': vital_heartrate,
                'user_id': user_id}
            # raise ContentNotFoundReturnData(user_id=user_id, data=data_dict)
            return data_dict

        return all_entries

    @token_auth.login_required
    @accepts(schema=HeartAssessmentSchema, api=ns)
    @responds(schema=HeartAssessmentSchema, status_code=201, api=ns)
    def post(self, user_id):
        """create a cardio assessment entry for user_id"""
        check_client_existence(user_id)

        data=request.get_json()
        data['user_id'] = user_id

        hr_schema = HeartAssessmentSchema()
        client_hr = hr_schema.load(data)
        db.session.add(client_hr)
        db.session.commit()
        
        return client_hr

    
@ns.route('/assessment/moxy/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class Moxy(BaseResource):    
    """GET and POST moxy assessments for the client"""

    @token_auth.login_required
    @responds(schema=MoxyAssessmentSchema(many=True), api=ns)
    def get(self, user_id):
        """returns all moxy assessment entries for the specified client"""
        check_client_existence(user_id)

        all_entries = MoxyAssessment.query.filter_by(user_id=user_id).order_by(MoxyAssessment.timestamp.asc()).all()
        
        return all_entries

    @token_auth.login_required
    @accepts(schema=MoxyAssessmentSchema, api=ns)
    @responds(schema=MoxyAssessmentSchema, status_code=201, api=ns)
    def post(self, user_id):
        """create a moxy assessment entry for user_id"""
        check_client_existence(user_id)

        data=request.get_json()
        data['user_id'] = user_id

        moxy_schema = MoxyAssessmentSchema()
        client_moxy = moxy_schema.load(data)
        db.session.add(client_moxy)
        db.session.commit()
        
        return client_moxy

@ns.route('/assessment/lungcapacity/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class LungCapacity(BaseResource):    
    """GET and POST moxy assessments for the client"""

    @token_auth.login_required
    @responds(schema=LungAssessmentSchema(many=True), api=ns)
    def get(self, user_id):
        """returns all lung capacity assessment entries for the specified client"""
        check_client_existence(user_id)

        all_entries = LungAssessment.query.filter_by(user_id=user_id).order_by(LungAssessment.timestamp.asc()).all()

        if len(all_entries) == 0:
            recent_physical = MedicalPhysicalExam.query.filter_by(user_id=user_id).order_by(MedicalPhysicalExam.idx.desc()).first()
            if not recent_physical:
                vital_weight=None
            else:
                vital_weight = recent_physical.vital_weight
            data_dict = {
                'vital_weight': vital_weight,
                'user_id': user_id}
            # raise ContentNotFoundReturnData(user_id=user_id, data=data_dict)
            return data_dict
        
        return all_entries

    @token_auth.login_required
    @accepts(schema=LungAssessmentSchema, api=ns)
    @responds(schema=LungAssessmentSchema, status_code=201, api=ns)
    def post(self, user_id):
        """create a lung capacity assessment entry for user_id"""
        check_client_existence(user_id)

        data=request.get_json()
        data['user_id'] = user_id

        lung_schema = LungAssessmentSchema()
        client_lung_capacity = lung_schema.load(data)
        db.session.add(client_lung_capacity)
        db.session.commit()
        
        return client_lung_capacity

@ns.route('/assessment/moxyrip/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MoxyRipAssessment(BaseResource):    
    """GET and POST moxy rip assessments for the client"""

    @token_auth.login_required
    @responds(schema=MoxyRipSchema(many=True), api=ns)
    def get(self, user_id):
        """returns all moxy rip assessment entries for the specified client"""
        check_client_existence(user_id)

        all_entries = MoxyRipTest.query.filter_by(user_id=user_id).order_by(MoxyRipTest.timestamp.asc()).all()

        if len(all_entries) == 0:
            recent_physical = MedicalPhysicalExam.query.filter_by(user_id=user_id).order_by(MedicalPhysicalExam.idx.desc()).first()
            if not recent_physical:
                vital_weight=None
            else:
                vital_weight = recent_physical.vital_weight
            data_dict = {
                'vital_weight': vital_weight,
                'user_id': user_id}
            # raise ContentNotFoundReturnData(user_id=user_id, data=data_dict)
            return data_dict
        
        return all_entries

    @token_auth.login_required
    @accepts(schema=MoxyRipSchema, api=ns)
    @responds(schema=MoxyRipSchema, status_code=201, api=ns)
    def post(self, user_id):
        """create a moxy rip assessment entry for user_id"""
        check_client_existence(user_id)

        data=request.get_json()
        data['user_id'] = user_id

        moxy_rip_schema = MoxyRipSchema()
        client_moxy_rip = moxy_rip_schema.load(data)
        db.session.add(client_moxy_rip)
        db.session.commit()
        
        return client_moxy_rip

@ns.route('/questionnaire/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class FitnessQuestionnaireEndpoint(BaseResource):
    """ Fitness questionnaire endpoint.

    One questionnaire per client.
    """

    @token_auth.login_required
    @responds(schema=FitnessQuestionnaireSchema, api=ns)
    def get(self, user_id):
        """ Returns a fitness questionnaire for user_id. """
        check_client_existence(user_id)

        quest = (
            FitnessQuestionnaire
            .query
            .filter_by(
                user_id=user_id)
            .one_or_none())

        return quest

    @token_auth.login_required
    @accepts(schema=FitnessQuestionnaireSchema, api=ns)
    @responds(status_code=201, api=ns)
    def post(self, user_id):
        """ Create a fitness questionnaire entry for user_id. """
        check_client_existence(user_id)

        request.parsed_obj.user_id = user_id
        db.session.add(request.parsed_obj)
        db.session.commit()
        
    @token_auth.login_required
    @accepts(schema=FitnessQuestionnaireSchema, api=ns)
    @responds(status_code=201, api=ns)
    def put(self, user_id):
        """ Update a fitness questionnaire entry for user_id. """
        check_client_existence(user_id)

        quest = (
            FitnessQuestionnaire
            .query
            .filter_by(
                user_id=user_id)
            .first())

        request.parsed_obj.idx = quest.idx
        request.parsed_obj.user_id = user_id
        db.session.merge(request.parsed_obj)
        db.session.commit()
