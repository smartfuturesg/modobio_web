import os, boto3, secrets, pathlib
from datetime import datetime

from flask import request, current_app
from flask_accepts import accepts, responds
from flask_restx import Resource, Api

from odyssey import db
from odyssey.models.client import ClientExternalMR
from odyssey.models.doctor import (
    MedicalPhysicalExam, 
    MedicalHistory, 
    MedicalBloodTests,
    MedicalBloodTestResults,
    MedicalBloodTestResultTypes, 
    MedicalImaging
)

from odyssey.models.misc import MedicalInstitutions
from odyssey.api import api
from odyssey.api.auth import token_auth
from odyssey.api.errors import (
    UserNotFound, 
    IllegalSetting, 
    ContentNotFound, 
    InputError
)
from .schemas import (
    ClientExternalMREntrySchema, 
    ClientExternalMRSchema, 
    MedicalHistorySchema, 
    MedicalPhysicalExamSchema, 
    MedicalInstitutionsSchema,
    MedicalBloodTestsInputSchema,
    MedicalBloodTestSchema,
    MedicalBloodTestResultsSchema,
    MedicalBloodTestResultsOutputSchema,
    MedicalBloodTestResultTypesSchema,
    MedicalImagingSchema
)
from odyssey.utils.misc import check_client_existence, check_blood_test_existence, check_blood_test_result_type_existence


ns = api.namespace('doctor', description='Operations related to doctor')


@ns.route('/images/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class MedImaging(Resource):
    @token_auth.login_required
    @responds(schema=MedicalImagingSchema(many=True), api=ns)
    def get(self, clientid):
        """returns a json file of all the medical images in the database for the specified clientid

            Note:
            image_path is a sharable url for an image saved in S3 Bucket,
            if running locally, it is the path to a local temp file
        """
        check_client_existence(clientid)
        data = MedicalImaging.query.filter_by(clientid=clientid).all()
        if not data:
            raise ContentNotFound()
        
        if not current_app.config['LOCAL_CONFIG']:
            bucket_name = current_app.config['S3_BUCKET_NAME']

            s3 = boto3.client('s3')
            params = {
                        'Bucket' : bucket_name,
                        'Key' : None
                    }
            for img in data:
                if img.image_path:
                    params['Key'] = img.image_path
                    url = s3.generate_presigned_url('get_object', Params=params, ExpiresIn=3600)
                    img.image_path = url
 
        return data

    #Unable to use @accepts because the input files come in a form-data, not json.
    @token_auth.login_required
    @responds(status_code=201, api=ns)
    def post(self, clientid):
        """For adding one or many medical images to the database for the specified clientid

        Expects form-data

        "image": (file_path , open(file_path, mode='rb'), 'Mime type')
        "image_date": "2020-09-25",
        "image_origin_location": "string",
        "image_type": "string",
        "image_read": "string",
        "image_path": "string"

        """
        check_client_existence(clientid)
        bucket_name = current_app.config['S3_BUCKET_NAME']

        #Verify at least 1 file with key-name:image is selected for upload
        if 'image' not in request.files:
            raise InputError(400, 'Empty input file')

        files = request.files #ImmutableMultiDict of key : FileStorage object
        mi_schema = MedicalImagingSchema()
        MAX_bytes = 524288000 #500 mb
        data_list = []
        hex_token = secrets.token_hex(4)
        
        for i, img in enumerate(files.getlist('image')):
            mi_data = mi_schema.load(request.form)
            mi_data.clientid = clientid
            date = mi_data.image_date

            #Verifying image size is within a safe threashold (MAX = 500 mb)
            img.seek(0, os.SEEK_END)
            img_size = img.tell()
            mi_data.image_size = img_size
            if img_size > MAX_bytes:
                raise InputError(413, 'File too large')

            #Rename image (format: imageType_Y-M-d_4digitRandomHex_index.img_extension) AND Save=>S3 
            img_extension = pathlib.Path(img.filename).suffix
            img.seek(0)

            if current_app.config['LOCAL_CONFIG']:
                path = pathlib.Path(bucket_name) / f'id{clientid:05d}' / 'medical_images'
                path.mkdir(parents=True, exist_ok=True)
                s3key = f'{mi_data.image_type}_{date}_{hex_token}_{i}{img_extension}'
                file_name = (path / s3key).as_posix()
                mi_data.image_path = file_name
                img.save(file_name)

            else:
                s3key = f'id{clientid:05d}/medical_images/{mi_data.image_type}_{date}_{hex_token}_{i}{img_extension}'
                s3 = boto3.resource('s3')
                s3.Bucket(bucket_name).put_object(Key= s3key, Body=img.stream) 
                mi_data.image_path = s3key  

            data_list.append(mi_data)

        db.session.add_all(data_list)  
        db.session.commit()

@ns.route('/bloodtest/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class MedBloodTest(Resource):
    @token_auth.login_required
    @responds(schema=MedicalBloodTestSchema(many=True), api=ns)
    def get(self, clientid):
        check_client_existence(clientid)
        blood_tests = MedicalBloodTests.query.filter_by(clientid=clientid).all()

        if not blood_tests:
            raise ContentNotFound()

        return blood_tests

    @token_auth.login_required
    @accepts(schema=MedicalBloodTestsInputSchema, api=ns)
    @responds(schema=MedicalBloodTestSchema, status_code=201, api=ns)
    def post(self, clientid):
        check_client_existence(clientid)
        data = request.get_json()

        #remove results from data, commit test info without results to db
        results = data['results']
        del data['results']
        data['clientid'] = clientid
        client_bt = MedicalBloodTestSchema().load(data)
        db.session.add(client_bt)
        db.session.commit()

        #insert results into the result table
        test = MedicalBloodTests.query.filter_by(testid=client_bt.testid).first()
        for result in results:
            check_blood_test_result_type_existence(result['result_name'])
            resultid = MedicalBloodTestResultTypes.query.filter_by(result_name=result['result_name']).first().resultid
            result_data = {'testid': client_bt.testid, 'resultid': resultid, 'result_value': result['result_value']}
            bt_result = MedicalBloodTestResultsSchema().load(result_data)
            db.session.add(bt_result)
        db.session.commit()
        return test

@ns.route('/bloodtest/results/<int:testid>/')
@ns.doc(params={'testid': 'Test ID number'})
class MedBloodTestResults(Resource):
    @token_auth.login_required
    @responds(schema=MedicalBloodTestResultsOutputSchema(many=True), api=ns)
    def get(self, testid):
        #query for join of MedicalBloodTestResults and MedicalBloodTestResultTypes tables
        check_blood_test_existence(testid)
        results = MedicalBloodTestResults.query.filter_by(testid=testid).all()

        #replace resultid with result name for readability      
        response = []
        for result in results:
            output = {'idx': result.idx,'testid': result.testid,'result_value': result.result_value}
            output['result_type'] = MedicalBloodTestResultTypes.query.filter_by(resultid=result.resultid).first().result_name
            response.append(output) 
        return response

@ns.route('/bloodtest/resulttypes/')
class MedBloodTestResultTypes(Resource):
    @token_auth.login_required
    @responds(schema=MedicalBloodTestResultTypesSchema(many=True), api=ns)
    def get(self):
        return MedicalBloodTestResultTypes.query.all()

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