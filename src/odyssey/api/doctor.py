
from datetime import datetime

from flask import request
from flask_accepts import accepts, responds
from flask_restx import Resource, Api

from odyssey import db
from odyssey.models.client import ClientExternalMR
from odyssey.models.doctor import MedicalPhysicalExam, MedicalHistory, MedicalBloodChemistryCMP
from odyssey.models.misc import MedicalInstitutions
from odyssey.api import api
from odyssey.api.auth import token_auth
from odyssey.api.errors import UserNotFound, IllegalSetting, ContentNotFound
from odyssey.utils.misc import check_client_existence
from odyssey.utils.schemas import (
    ClientExternalMREntrySchema, 
    ClientExternalMRSchema, 
    MedicalHistorySchema, 
    MedicalPhysicalExamSchema, 
    MedicalInstitutionsSchema,
    BloodChemistryCMPSchema
)

ns = api.namespace('doctor', description='Operations related to doctor')

@ns.route('/bloodtest/cmp/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class MedBloodChemistryCMP(Resource):
    """
       Records client's Comprehensive Metabolic Panel Blood Test Results
    """
    @ns.doc(security='apikey')
    @token_auth.login_required
    @responds(schema=BloodChemistryCMPSchema(many=True), api=ns)
    def get(self,clientid):
        """ Returns client's historical CMP results """
        
        check_client_existence(clientid)
        data = MedicalBloodChemistryCMP.query.filter_by(clientid=clientid).all()
        if not data:
            raise ContentNotFound()
        return data

    @token_auth.login_required
    @accepts(schema=BloodChemistryCMPSchema, api=ns)
    @ns.doc(security='apikey')
    @responds(schema=BloodChemistryCMPSchema, api=ns, status_code=201)
    def post(self,clientid):
        """create new db entItry for CMP"""
        check_client_existence(clientid)
        data = request.get_json()
        data["clientid"] = clientid
        data["bunByAlbumin"] = data['bun']/data['albumin']
        cmp_schema = BloodChemistryCMPSchema()
        cmp_data = cmp_schema.load(data)
        db.session.add(cmp_data)
        db.session.commit()
        return cmp_data

    @token_auth.login_required
    @accepts(schema=BloodChemistryCMPSchema, api=ns)
    @responds(schema=BloodChemistryCMPSchema, api=ns)
    def put(self, clientid):
        """ updates client's CMP test input based on index """
        check_client_existence(clientid)
        # get payload and update the current instance followd by db commit
        data = request.get_json()
        cmp_data = MedicalBloodChemistryCMP.query.filter_by(idx=data['idx']).one_or_none()

        if not cmp_data:
            raise ExamNotFound(data['idx'])
        
        # update resource
        data["bunByAlbumin"] = data['bun']/data['albumin']
        cmp_data.update(data)
        db.session.commit()

        return cmp_data

@ns.route('/medicalhistory/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class MedHistory(Resource):
    @token_auth.login_required
    @responds(schema=MedicalHistorySchema, api=ns)
    def get(self, clientid):
        """returns client's medical history as a json for the clientid specified"""
        check_client_existence(clientid)

        client = MedicalHistory.query.filter_by(clientid=clientid).first()

        if not client:
            raise ContentNotFound()

        return client

    @token_auth.login_required
    @accepts(schema=MedicalHistorySchema, api=ns)
    @responds(schema=MedicalHistorySchema, status_code=201, api=ns)
    def post(self, clientid):
        """returns client's medical history as a json for the clientid specified"""
        check_client_existence(clientid)

        current_med_history = MedicalHistory.query.filter_by(clientid=clientid).first()
        
        if current_med_history:
            raise IllegalSetting(message=f"Medical History for clientid {clientid} already exists. Please use PUT method")


        data = request.get_json()
        data["clientid"] = clientid

        mh_schema = MedicalHistorySchema()

        client_mh = mh_schema.load(data)

        db.session.add(client_mh)
        db.session.commit()

        return client_mh

    @token_auth.login_required
    @accepts(schema=MedicalHistorySchema, api=ns)
    @responds(schema=MedicalHistorySchema, api=ns)
    def put(self, clientid):
        """updates client's medical history as a json for the clientid specified"""
        check_client_existence(clientid)

        client_mh = MedicalHistory.query.filter_by(clientid=clientid).first()

        if not client_mh:
            raise UserNotFound(clientid, message = f"The client with id: {clientid} does not yet have a medical history in the database")
        
        # get payload and update the current instance followd by db commit
        data = request.get_json()
        
        data['last_examination_date'] = datetime.strptime(data['last_examination_date'], "%Y-%m-%d")
        
        # update resource 
        client_mh.update(data)

        db.session.commit()

        return client_mh


@ns.route('/physical/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class MedPhysical(Resource):
    @token_auth.login_required
    @responds(schema=MedicalPhysicalExamSchema(many=True), api=ns)
    def get(self, clientid):
        """returns client's medical physical exam as a json for the clientid specified"""
        check_client_existence(clientid)

        client = MedicalPhysicalExam.query.filter_by(clientid=clientid).order_by(MedicalPhysicalExam.timestamp.asc()).all()

        if not client:
            raise ContentNotFound()

        return client

    @token_auth.login_required
    @accepts(schema=MedicalPhysicalExamSchema, api=ns)
    @responds(schema=MedicalPhysicalExamSchema, status_code=201, api=ns)
    def post(self, clientid):
        """creates new db entry of client's medical physical exam as a json for the clientid specified"""
        check_client_existence(clientid)

        data = request.get_json()
        data["clientid"] = clientid
        data["timestamp"] = datetime.utcnow().isoformat()

        mh_schema = MedicalPhysicalExamSchema()

        client_mp = mh_schema.load(data)

        db.session.add(client_mp)
        db.session.commit()

        return client_mp

@ns.route('/medicalinstitutions/')
class AllMedInstitutes(Resource):
    @token_auth.login_required
    @responds(schema=MedicalInstitutionsSchema(many=True), api=ns)
    def get(self):
        """returns all medical institutes currently in the database"""

        institutes = MedicalInstitutions.query.all()
        
        return institutes

@ns.route('/medicalinstitutions/recordid/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class ExternalMedicalRecordIDs(Resource):
    @token_auth.login_required
    @accepts(schema=ClientExternalMREntrySchema,  api=ns)
    @responds(schema=ClientExternalMREntrySchema,status_code=201, api=ns)
    def post(self, clientid):
        """for submitting client medical record ids from external medical institutions"""

        data = request.get_json()
        # check for new institute names. If the institute_id is 9999, then enter 
        # the new institute into the dabase before proceeding
        data_cleaned = []
        for record in data['record_locators']:
            record["clientid"] = clientid # add in the clientid
            if record["institute_id"] == 9999 and len(record["institute_name"]) > 0:
                # enter new insitute name into database
                new_institute = MedicalInstitutions(institute_name = record["institute_name"])
                db.session.add(new_institute)
                db.session.commit()
                record["institute_id"] = new_institute.institute_id

            data_cleaned.append(record)
            
        client_med_record_ids = ClientExternalMRSchema(many=True).load(data_cleaned)
        
        db.session.add_all(client_med_record_ids)
        db.session.commit()
        
        return client_med_record_ids

    @token_auth.login_required
    @responds(schema=ClientExternalMREntrySchema, api=ns)
    def get(self, clientid):
        """returns all medical record ids for clientid"""

        client_med_record_ids = ClientExternalMR.query.filter_by(clientid=clientid).all()

        return client_med_record_ids
    
    

