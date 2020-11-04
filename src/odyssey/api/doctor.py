import os, boto3, secrets, pathlib
from datetime import datetime

from flask import request, current_app, jsonify
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
from odyssey.models.staff import Staff
from odyssey.api import api
from odyssey.utils.auth import token_auth

# from odyssey.api.auth import token_auth
from odyssey.api.errors import (
    UserNotFound, 
    IllegalSetting, 
    ContentNotFound, 
    ExamNotFound, 
    InputError,
    InsufficientInputs,
    MethodNotAllowed,
    UnknownError
)
from odyssey.utils.misc import check_client_existence, check_blood_test_existence, check_blood_test_result_type_existence
from odyssey.utils.schemas import (
    AllMedicalBloodTestSchema,
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
        query = db.session.query(
                    MedicalImaging, Staff.firstname, Staff.lastname
                ).filter(
                    MedicalImaging.clientid == clientid
                ).filter(
                    MedicalImaging.reporter_id == Staff.staffid
                ).all()
        
        # if no tests have been submitted
        if not query:
            raise ContentNotFound()
        
        # prepare response with reporter info
        response = []
        for data in query:
            img_dat = data[0].__dict__
            img_dat.update({'reporter_firstname': data[1], 'reporter_lastname': data[2]})
            response.append(img_dat)

        if not current_app.config['LOCAL_CONFIG']:
            bucket_name = current_app.config['S3_BUCKET_NAME']

            s3 = boto3.client('s3')
            params = {
                        'Bucket' : bucket_name,
                        'Key' : None
                    }
            for img in response:
                if img.image_path:
                    params['Key'] = img.image_path
                    url = s3.generate_presigned_url('get_object', Params=params, ExpiresIn=3600)
                    img.image_path = url
 
        return response

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

        # bring up reporting staff member
        reporter = token_auth.current_user()
        mi_schema = MedicalImagingSchema()
        #Verify at least 1 file with key-name:image is selected for upload
        if 'image' not in request.files:
            mi_data = mi_schema.load(request.form)
            mi_data.clientid = clientid
            mi_data.reporter_id = reporter.staffid
            db.session.add(mi_data)
            db.session.commit()
            return 

        files = request.files #ImmutableMultiDict of key : FileStorage object
        MAX_bytes = 524288000 #500 mb
        data_list = []
        hex_token = secrets.token_hex(4)
        
        for i, img in enumerate(files.getlist('image')):
            mi_data = mi_schema.load(request.form)
            mi_data.clientid = clientid
            mi_data.reporter_id = reporter.staffid
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
    @accepts(schema=MedicalBloodTestsInputSchema, api=ns)
    @responds(schema=MedicalBloodTestSchema, status_code=201, api=ns)
    def post(self, clientid):
        """
        Resource to submit a new blood test instance for the specified client.

        Test submissions are given a testid which can be used to reference back
        to the results related to this submisison. Each submission may have 
        multiple results (e.g. in a panel)
        """
        check_client_existence(clientid)
        data = request.get_json()

        # remove results from data, commit test info without results to db
        results = data['results']
        del data['results']
        data['clientid'] = clientid
        data['reporter_id'] = token_auth.current_user().staffid
        client_bt = MedicalBloodTestSchema().load(data)
        
        db.session.add(client_bt)
        db.session.flush()

        # insert results into the result table
        for result in results:
            check_blood_test_result_type_existence(result['result_name'])
            resultid = MedicalBloodTestResultTypes.query.filter_by(result_name=result['result_name']).first().resultid
            result_data = {'testid': client_bt.testid, 
                           'resultid': resultid, 
                           'result_value': result['result_value']}
            db.session.add(MedicalBloodTestResultsSchema().load(result_data))
        
        db.session.commit()
        return client_bt

@ns.route('/bloodtest/all/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class MedBloodTest(Resource):
    @token_auth.login_required
    @responds(schema=AllMedicalBloodTestSchema, api=ns)
    def get(self, clientid):
        """
        This resource returns every instance of blood test submissions for the 
        specified clientid

        Test submissions relate overall submission data: testid, date, notes, panel_type
        to the actual results. Each submission may have multiple results
        where the results can be referenced by the testid provided in this request
        """
        check_client_existence(clientid)
        blood_tests =  db.session.query(
                    MedicalBloodTests, Staff.firstname, Staff.lastname
                ).filter(
                    MedicalBloodTests.reporter_id == Staff.staffid
                ).filter(
                    MedicalBloodTests.clientid == clientid
                ).all()

        if not blood_tests:
            raise ContentNotFound()
        # prepare response items with reporter name from Staff table
        response = []
        for test in blood_tests:
            data = test[0].__dict__
            data.update({'reporter_firstname': test[1], 'reporter_lastname': test[2]})
            response.append(data)
        payload = {}
        payload['items'] = response
        payload['total'] = len(blood_tests)
        payload['clientid'] = clientid
        return payload


@ns.route('/bloodtest/results/<int:testid>/')
@ns.doc(params={'testid': 'Test ID number'})
class MedBloodTestResults(Resource):
    """
    Resource for working with a single blood test 
    entry instance, testid.

    Each test instance may have multiple test results. 
    """
    @token_auth.login_required
    @responds(schema=MedicalBloodTestResultsOutputSchema, api=ns)
    def get(self, testid):
        """
        Returns details of the test denoted by testid as well as 
        the actual results submitted.
        """
        #query for join of MedicalBloodTestResults and MedicalBloodTestResultTypes tables
        check_blood_test_existence(testid)
        results =  db.session.query(
                MedicalBloodTests, MedicalBloodTestResults, MedicalBloodTestResultTypes, Staff
                ).join(
                    MedicalBloodTestResultTypes
                ).join(MedicalBloodTests
                ).filter(
                    MedicalBloodTests.testid == MedicalBloodTestResults.testid
                ).filter(
                    MedicalBloodTests.testid==testid
                ).filter(
                    MedicalBloodTests.reporter_id == Staff.staffid
                ).all()
        if len(results) == 0:
            raise ContentNotFound()
        
        # prepare response with test details   
        nested_results = {'testid': testid, 
                          'date' : results[0][0].date,
                          'notes' : results[0][0].notes,
                          'panel_type' : results[0][0].panel_type,
                          'reporter_id': results[0][0].reporter_id,
                          'reporter_firstname': results[0][3].firstname,
                          'reporter_lastname': results[0][3].lastname,
                          'results': []} 
        
        # loop through results in order to nest results in their respective test
        # entry instances (testid)
        for _, test_result, result_type, _ in results:
                res = {'result_name': result_type.result_name, 
                        'result_value': test_result.result_value,
                        'evaluation': test_result.evaluation}
                nested_results['results'].append(res)

        payload = {}
        payload['items'] = [nested_results]
        payload['tests'] = 1
        payload['test_results'] = len( nested_results['results'])
        payload['clientid'] = results[0][0].clientid
        return payload

@ns.route('/bloodtest/results/all/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class AllMedBloodTestResults(Resource):
    """
    Endpoint for returning all blood test results from a client
    """
    @token_auth.login_required
    @responds(schema=MedicalBloodTestResultsOutputSchema, api=ns)
    def get(self, clientid):
        # pull up all tests, test results, and the test type names for this client
        results =  db.session.query(
                        MedicalBloodTests, MedicalBloodTestResults, MedicalBloodTestResultTypes, Staff
                        ).join(
                            MedicalBloodTestResultTypes
                        ).join(MedicalBloodTests
                        ).filter(
                            MedicalBloodTests.testid == MedicalBloodTestResults.testid
                        ).filter(
                            MedicalBloodTests.clientid==clientid
                        ).filter(
                            MedicalBloodTests.reporter_id == Staff.staffid
                        ).all()

        test_ids = set([(x[0].testid, x[0].reporter_id, x[3].firstname, x[3].lastname) for x in results])
        nested_results = [{'testid': x[0], 'reporter_id': x[1], 'reporter_firstname': x[2], 'reporter_lastname': x[3], 'results': []} for x in test_ids ]
        
        # loop through results in order to nest results in their respective test
        # entry instances (testid)
        for test_info, test_result, result_type, _ in results:
            for test in nested_results:
                # add rest result to appropriate test entry instance (testid)
                if test_result.testid == test['testid']:
                    res = {'result_name': result_type.result_name, 
                           'result_value': test_result.result_value,
                           'evaluation': test_result.evaluation}
                    test['results'].append(res)
                    # add test details if not present
                    if not test.get('date', False):
                        test['date'] = test_info.date
                        test['notes'] = test_info.notes
                        test['panel_type'] = test_info.panel_type
        payload = {}
        payload['items'] = nested_results
        payload['tests'] = len(test_ids)
        payload['test_results'] = len(results)
        payload['clientid'] = clientid
        return payload


@ns.route('/bloodtest/result-types/')
class MedBloodTestResultTypes(Resource):
    """
    Returns the types of tests currently documented in the DB
    """
    @token_auth.login_required
    @responds(schema=MedicalBloodTestResultTypesSchema, api=ns)
    def get(self):
        bt_types = MedicalBloodTestResultTypes.query.all()
        payload = {'items' : bt_types, 'total' : len(bt_types)}
        return payload

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
        """returns all client's medical physical exams for the clientid specified"""
        check_client_existence(clientid)

        query =  db.session.query(
                MedicalPhysicalExam, Staff.firstname, Staff.lastname
                ).filter(
                    MedicalPhysicalExam.clientid == clientid
                ).filter(
                    MedicalPhysicalExam.reporter_id == Staff.staffid
                ).all()

        if not query:
            raise ContentNotFound()
        # prepare response with staff name and medical physical data
        response = []
        for data in query:
            physical = data[0].__dict__    
            physical.update({'reporter_firstname': data[1], 'reporter_lastname': data[2]})
            response.append(physical)

        return response

    @token_auth.login_required
    @accepts(schema=MedicalPhysicalExamSchema, api=ns)
    @responds(schema=MedicalPhysicalExamSchema, status_code=201, api=ns)
    def post(self, clientid):
        """creates new db entry of client's medical physical exam as a json for the clientid specified"""
        check_client_existence(clientid)

        data = request.get_json()
        data["clientid"] = clientid

        client_mp = MedicalPhysicalExamSchema().load(data)

        # look up the reporting staff member and add their id to the 
        # client's physical entry
        reporter = token_auth.current_user()
        client_mp.reporter_id = reporter.staffid

        # prepare api response with reporter name
        response = client_mp.__dict__.copy()
        response["reporter_firstname"] = reporter.firstname
        response["reporter_lastname"] = reporter.lastname

        db.session.add(client_mp)
        db.session.commit()
        return response

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