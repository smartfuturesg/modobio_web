from datetime import datetime

from flask import request
from flask_accepts import accepts, responds
from flask_restx import Resource, Api

from odyssey import db
from odyssey.models.client import ClientExternalMR
from odyssey.models.doctor import MedicalPhysicalExam, MedicalHistory, MedicalBloodChemistryCBC, MedicalBloodChemistryThyroid, MedicalBloodChemistryCMP, MedicalBloodChemistryLipids
from odyssey.models.misc import MedicalInstitutions
from odyssey.api import api
from odyssey.api.auth import token_auth
from odyssey.api.errors import UserNotFound, IllegalSetting, ContentNotFound, ExamNotFound, InsufficientInputs, MethodNotAllowed
from odyssey.utils.misc import check_client_existence
from odyssey.utils.schemas import (
    ClientExternalMREntrySchema, 
    ClientExternalMRSchema, 
    MedicalHistorySchema, 
    MedicalPhysicalExamSchema, 
    MedicalInstitutionsSchema,
    BloodChemistryCMPSchema,
    BloodChemistryCBCSchema,
    MedicalBloodChemistryThyroidSchema,
    MedicalBloodChemistryLipidsSchema
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


@ns.route('/bloodtest/cbc/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class MedBloodChemistryCBC(Resource):
    """
       Records client's Complete Blood Count Blood Test Results
    """

    @ns.doc(security='apikey')
    @token_auth.login_required
    @responds(schema=BloodChemistryCBCSchema(many=True), api=ns)
    def get(self,clientid):
        """ Returns client's historical CBC results """
        
        check_client_existence(clientid)

        data = MedicalBloodChemistryCBC.query.filter_by(clientid=clientid).all()
        if not data:
            raise ContentNotFound()
        return data

    @token_auth.login_required
    @accepts(schema=BloodChemistryCBCSchema, api=ns)
    @ns.doc(security='apikey')
    @responds(schema=BloodChemistryCBCSchema, api=ns, status_code=201)
    def post(self,clientid):
        check_client_existence(clientid)
        """create new db entry for CBC"""
        data = request.get_json()
        temp_date = data['exam_date']
        del data['exam_date']

        # Check if data is empty
        if not data:
            # Data has nothing in it, raise error.
            # Blood Chemistry test needs at least one input
            raise InsufficientInputs()

        data['exam_date'] = temp_date  
        data["clientid"] = clientid
        
        """ Additional ratio calculations from payload """
        if 'abs_lymphocytes' in data:
            if 'platelets' in data:
                data['plateletsByLymphocyte'] = data['platelets']/data['abs_lymphocytes']
            if 'abs_neutrophils' in data:
                data['neutrophilByLymphocyte'] = data['abs_neutrophils']/data['abs_lymphocytes']
            if 'abs_monocytes' in data:
                data['lymphocyteByMonocyte'] = data['abs_lymphocytes']/data['abs_monocytes']
        if 'platelets' in data and 'mch' in data:
            data['plateletsByMch'] = data['platelets']/data['mch']

        cbc_schema = BloodChemistryCBCSchema()
        cbc_data = cbc_schema.load(data)
        db.session.add(cbc_data)
        db.session.commit()
        return cbc_data

    @token_auth.login_required
    @accepts(schema=BloodChemistryCBCSchema, api=ns)
    @responds(schema=BloodChemistryCBCSchema, api=ns)
    def put(self, clientid):
        """ updates client's CMP test input based on index """
        check_client_existence(clientid)
        # get payload and update the current instance followd by db commit
        data = request.get_json()
        cbc_data = MedicalBloodChemistryCBC.query.filter_by(idx=data['idx']).one_or_none()

        if not cbc_data:
            raise ExamNotFound(data['idx'])

        temp_date = data['exam_date']
        temp_idx = data['idx']
        del data['exam_date']
        del data['idx']
        # Check if data is empty
        if not data:
            # Data has nothing in it, raise error.
            # Blood Chemistry test needs at least one input
            raise InsufficientInputs()

        data['exam_date'] = temp_date  
        data["idx"] = temp_idx

        """ Additional ratio calculations from payload """
        if 'abs_lymphocytes' in data:
            if 'platelets' in data:
                data['plateletsByLymphocyte'] = data['platelets']/data['abs_lymphocytes']
            if 'abs_neutrophils' in data:
                data['neutrophilByLymphocyte'] = data['abs_neutrophils']/data['abs_lymphocytes']
            if 'abs_monocytes' in data:
                data['lymphocyteByMonocyte'] = data['abs_lymphocytes']/data['abs_monocytes']
        if 'platelets' in data and 'mch' in data:
            data['plateletsByMch'] = data['platelets']/data['mch']
        cbc_data.update(data)
        db.session.commit()

        return cbc_data


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
    
    

@ns.route('/bloodchemistry/thyroid/<int:clientid>/')
@ns.doc(params={'clientId': 'Client ID number'})
class MedBloodChemistryThyroid(Resource):
    @token_auth.login_required
    @responds(schema=MedicalBloodChemistryThyroidSchema(many=True), api=ns)
    def get(self, clientid):
        """returns all blood thyroid results as a json for the client ID specified"""
        check_client_existence(clientid)

        exams = MedicalBloodChemistryThyroid.query.filter_by(clientid=clientid).all()

        if not exams:
            raise ContentNotFound()

        return exams
    
    @token_auth.login_required
    @accepts(schema=MedicalBloodChemistryThyroidSchema, api=ns)
    @responds(schema=MedicalBloodChemistryThyroidSchema, status_code=201, api=ns)
    def post(self, clientid):
        """creates new db entry for blood test results as a json for the blood exam ID specified"""
        check_client_existence(clientid)

        data = request.get_json()

        #temporarily remove exam date to check if at least 1 other field is populated
        temp_date = data["exam_date"]
        del data["exam_date"]
        if not data:
            #there is not at least 1 other field populated, illegal input
            raise InsufficientInputs("At least 1 input other than date is required")
        
        #at least 1 other field is populated, restore exam date and idx and resume PUT
        data["exam_date"] = temp_date
        data["clientid"] = clientid

        bt_schema = MedicalBloodChemistryThyroidSchema()

        client_bt = bt_schema.load(data)

        db.session.add(client_bt)
        db.session.commit()

        return client_bt

    @token_auth.login_required
    @accepts(schema=MedicalBloodChemistryThyroidSchema, api=ns)
    @responds(schema=MedicalBloodChemistryThyroidSchema, api=ns)
    def put(self, clientid):
        """edit exam info"""
        # get payload
        data = request.get_json()

        if 'idx' not in data.keys():
            raise ExamNotFound('None')

        exam = MedicalBloodChemistryThyroid.query.filter_by(idx=data['idx']).first()

        #check that exam at given idx exists
        if not exam:
            raise ExamNotFound(data['idx'])

        #temporarily remove exam date and idx to check if at least 1 other field is populated
        temp_date = data["exam_date"]
        temp_idx = data["idx"]
        del(data["exam_date"])
        del(data["idx"])
        if not data:
            #there is not at least 1 other field populated, illegal input
            raise InsufficientInputs("At least 1 input other than date and idx is required")

        #at least 1 other field is populated, restore exam date and idx and resume PUT
        data["exam_date"] = temp_date
        data["idx"] = temp_idx

        data['exam_date'] = datetime.strptime(data['exam_date'], "%Y-%m-%d")

        # update resource 
        exam.update(data)

        db.session.commit()

        return exam

@ns.route('/bloodchemistry/lipids/<int:clientid>/')
@ns.doc(params={'clientId': 'Client ID number'})
class MedBloodChemistryLipids(Resource):
    @token_auth.login_required
    @responds(schema=MedicalBloodChemistryLipidsSchema(many=True), api=ns)
    def get(self, clientid):
        """returns all blood thyroid results as a json for the client ID specified"""
        check_client_existence(clientid)

        exams = MedicalBloodChemistryLipids.query.filter_by(clientid=clientid).all()

        if not exams:
            raise ContentNotFound()

        return exams
    
    @token_auth.login_required
    @accepts(schema=MedicalBloodChemistryLipidsSchema, api=ns)
    @responds(schema=MedicalBloodChemistryLipidsSchema, status_code=201, api=ns)
    def post(self, clientid):
        """creates new db entry for blood test results as a json for the blood exam ID specified"""
        check_client_existence(clientid)

        data = request.get_json()

        #temporarily remove exam date and idx to check if at least 1 other field is populated
        temp_date = data["exam_date"]
        del data["exam_date"]
        if not data:
            #there is not at least 1 other field populated, illegal input
            raise InsufficientInputs("At least 1 input other than date and idx is required")

        #at least 1 other field is populated, restore exam date and resume POST
        data["exam_date"] = temp_date
        data['clientid'] = clientid

        #calculated values
        if 'cholesterol_hdl' in data.keys() and data['cholesterol_hdl'] != 0:
            data['cholesterol_over_hdl'] = data['cholesterol_total'] / data['cholesterol_hdl']
            data['ldl_over_hdl'] = data['cholesterol_ldl'] / data['cholesterol_hdl']
            data['triglycerides_over_hdl'] = data['triglycerides'] / data['cholesterol_hdl']
        

        bt_schema = MedicalBloodChemistryLipidsSchema()

        client_bt = bt_schema.load(data)

        db.session.add(client_bt)
        db.session.commit()

        return client_bt

    @token_auth.login_required
    @accepts(schema=MedicalBloodChemistryLipidsSchema, api=ns)
    @responds(schema=MedicalBloodChemistryLipidsSchema, api=ns)
    def put(self, clientid):
        """edit exam info"""
        # get payload
        data = request.get_json()

        if 'idx' not in data.keys():
            raise ExamNotFound('None')

        exam = MedicalBloodChemistryLipids.query.filter_by(idx=data['idx']).first()

        if not exam:
            raise ExamNotFound(data['idx'])
        
        #temporarily remove exam date and idx to check if at least 1 other field is populated
        temp_date = data["exam_date"]
        temp_idx = data["idx"]
        del(data["exam_date"])
        del(data["idx"])
        if not data:
            #there is not at least 1 other field populated, illegal input
            raise InsufficientInputs("At least 1 input other than date and idx is required")

        #at least 1 other field is populated, restore exam date and idx and resume PUT
        data["exam_date"] = temp_date
        data["idx"] = temp_idx
        data['exam_date'] = datetime.strptime(data['exam_date'], "%Y-%m-%d")
        
        #calculated values
        if 'cholesterol_hdl' in data.keys() and data['cholesterol_hdl'] != 0:
            data['cholesterol_over_hdl'] = data['cholesterol_total'] / data['cholesterol_hdl']
            data['ldl_over_hdl'] = data['cholesterol_ldl'] / data['cholesterol_hdl']
            data['triglycerides_over_hdl'] = data['triglycerides'] / data['cholesterol_hdl']

        # update resource 
        exam.update(data)

        db.session.commit()

        return exam
