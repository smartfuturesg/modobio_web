import os, boto3, secrets, pathlib
from datetime import datetime

from flask import request, current_app, jsonify
from flask_accepts import accepts, responds
from flask_restx import Resource, Api

from odyssey import db
from odyssey.models.client import ClientExternalMR, ClientSurgeries
from odyssey.models.doctor import (
    MedicalPhysicalExam, 
    MedicalHistory, 
    MedicalBloodTests,
    MedicalBloodTestResults,
    MedicalBloodTestResultTypes, 
    MedicalImaging
)

from odyssey.models.misc import MedicalInstitutions
from odyssey.models.user import User
from odyssey.api import api
from odyssey.utils.auth import token_auth

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
from odyssey.utils.misc import check_client_existence, check_staff_existence, check_blood_test_existence, check_blood_test_result_type_existence
from odyssey.utils.schemas import (
    AllMedicalBloodTestSchema,
    ClientExternalMREntrySchema, 
    ClientExternalMRSchema,
    ClientSurgeriesSchema,
    MedicalHistorySchema, 
    MedicalPhysicalExamSchema, 
    MedicalInstitutionsSchema,
    MedicalBloodTestsInputSchema,
    MedicalBloodTestSchema,
    MedicalBloodTestResultsSchema,
    MedicalBloodTestResultsOutputSchema,
    MedicalBloodTestResultTypesSchema,
    MedicalImagingSchema,
    JustUserIdSchema
)
from odyssey.constants import MEDICAL_CONDITIONS

ns = api.namespace('doctor', description='Operations related to doctor')


@ns.route('/images/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedImaging(Resource):
    @token_auth.login_required
    @responds(schema=MedicalImagingSchema(many=True), api=ns)
    def get(self, user_id):
        """returns a json file of all the medical images in the database for the specified user_id

            Note:
            image_path is a sharable url for an image saved in S3 Bucket,
            if running locally, it is the path to a local temp file
        """
        check_client_existence(user_id)
        query = db.session.query(
                    MedicalImaging, User.firstname, User.lastname
                ).filter(
                    MedicalImaging.user_id == user_id
                ).filter(
                    MedicalImaging.reporter_id == User.user_id
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
    def post(self, user_id):
        """For adding one or many medical images to the database for the specified user_id

        Expects form-data

        "image": (file_path , open(file_path, mode='rb'), 'Mime type')
        "image_date": "2020-09-25",
        "image_origin_location": "string",
        "image_type": "string",
        "image_read": "string",
        "image_path": "string"

        """
        check_client_existence(user_id)
        bucket_name = current_app.config['S3_BUCKET_NAME']

        # bring up reporting staff member
        reporter = token_auth.current_user()[0]
        mi_schema = MedicalImagingSchema()
        #Verify at least 1 file with key-name:image is selected for upload
        if 'image' not in request.files:
            mi_data = mi_schema.load(request.form)
            mi_data.user_id = user_id
            mi_data.reporter_id = reporter.user_id
            db.session.add(mi_data)
            db.session.commit()
            return 

        files = request.files #ImmutableMultiDict of key : FileStorage object
        MAX_bytes = 524288000 #500 mb
        data_list = []
        hex_token = secrets.token_hex(4)
        
        for i, img in enumerate(files.getlist('image')):
            mi_data = mi_schema.load(request.form)
            mi_data.user_id = user_id
            mi_data.reporter_id = reporter.user_id
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
                path = pathlib.Path(bucket_name) / f'id{user_id:05d}' / 'medical_images'
                path.mkdir(parents=True, exist_ok=True)
                s3key = f'{mi_data.image_type}_{date}_{hex_token}_{i}{img_extension}'
                file_name = (path / s3key).as_posix()
                mi_data.image_path = file_name
                img.save(file_name)

            else:
                s3key = f'id{user_id:05d}/medical_images/{mi_data.image_type}_{date}_{hex_token}_{i}{img_extension}'
                s3 = boto3.resource('s3')
                s3.Bucket(bucket_name).put_object(Key= s3key, Body=img.stream) 
                mi_data.image_path = s3key  

            data_list.append(mi_data)

        db.session.add_all(data_list)  
        db.session.commit()

@ns.route('/bloodtest/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedBloodTest(Resource):
    @token_auth.login_required
    @responds(schema=MedicalBloodTestSchema(many=True), api=ns)
    def get(self, user_id):
        #
        # ?? DEAD CODE ?? replaced by /bloodtest/all/user_id/ ?
        #
        check_client_existence(user_id)
        blood_tests = MedicalBloodTests.query.filter_by(user_id=user_id).all()

        if not blood_tests:
            raise ContentNotFound()

        return blood_tests

    @token_auth.login_required
    @accepts(schema=MedicalBloodTestsInputSchema, api=ns)
    @responds(schema=MedicalBloodTestSchema, status_code=201, api=ns)
    def post(self, user_id):
        """
        Resource to submit a new blood test instance for the specified client.

        Test submissions are given a test_id which can be used to reference back
        to the results related to this submisison. Each submission may have 
        multiple results (e.g. in a panel)
        """
        check_client_existence(user_id)
        data = request.get_json()
        
        # remove results from data, commit test info without results to db
        results = data['results']
        del data['results']
        data['user_id'] = user_id
        data['reporter_id'] = token_auth.current_user()[0].user_id
        client_bt = MedicalBloodTestSchema().load(data)
        
        db.session.add(client_bt)
        db.session.flush()

        # insert results into the result table
        for result in results:
            check_blood_test_result_type_existence(result['result_name'])
            result_id = MedicalBloodTestResultTypes.query.filter_by(result_name=result['result_name']).first().result_id
            result_data = {'test_id': client_bt.test_id, 
                           'result_id': result_id, 
                           'result_value': result['result_value']}
            db.session.add(MedicalBloodTestResultsSchema().load(result_data))
        
        db.session.commit()
        return client_bt

@ns.route('/bloodtest/all/<int:user_id>/')
@ns.doc(params={'user_id': 'Client ID number'})
class MedBloodTestAll(Resource):
    @token_auth.login_required
    @responds(schema=AllMedicalBloodTestSchema, api=ns)
    def get(self, user_id):
        """
        This resource returns every instance of blood test submissions for the 
        specified user_id

        Test submissions relate overall submission data: test_id, date, notes, panel_type
        to the actual results. Each submission may have multiple results
        where the results can be referenced by the test_id provided in this request
        """
        check_client_existence(user_id)
        blood_tests =  db.session.query(
                    MedicalBloodTests, User.firstname, User.lastname
                ).filter(
                    MedicalBloodTests.reporter_id == User.user_id
                ).filter(
                    MedicalBloodTests.user_id == user_id
                ).all()

        if not blood_tests:
            raise ContentNotFound()
        # prepare response items with reporter name from User table
        response = []
        for test in blood_tests:
            data = test[0].__dict__
            data.update({'reporter_firstname': test[1], 'reporter_lastname': test[2]})
            response.append(data)
        payload = {}
        payload['items'] = response
        payload['total'] = len(blood_tests)
        payload['user_id'] = user_id
        return payload


@ns.route('/bloodtest/results/<int:test_id>/')
@ns.doc(params={'test_id': 'Test ID number'})
class MedBloodTestResults(Resource):
    """
    Resource for working with a single blood test 
    entry instance, test_id.

    Each test instance may have multiple test results. 
    """
    @token_auth.login_required
    @responds(schema=MedicalBloodTestResultsOutputSchema, api=ns)
    def get(self, test_id):
        """
        Returns details of the test denoted by test_id as well as 
        the actual results submitted.
        """
        #query for join of MedicalBloodTestResults and MedicalBloodTestResultTypes tables
        check_blood_test_existence(test_id)
        results =  db.session.query(
                MedicalBloodTests, MedicalBloodTestResults, MedicalBloodTestResultTypes, User
                ).join(
                    MedicalBloodTestResultTypes
                ).join(MedicalBloodTests
                ).filter(
                    MedicalBloodTests.test_id == MedicalBloodTestResults.test_id
                ).filter(
                    MedicalBloodTests.test_id==test_id
                ).filter(
                    MedicalBloodTests.reporter_id == User.user_id
                ).all()
        if len(results) == 0:
            raise ContentNotFound()
        
        # prepare response with test details   
        nested_results = {'test_id': test_id, 
                          'date' : results[0][0].date,
                          'notes' : results[0][0].notes,
                          'panel_type' : results[0][0].panel_type,
                          'reporter_id': results[0][0].reporter_id,
                          'reporter_firstname': results[0][3].firstname,
                          'reporter_lastname': results[0][3].lastname,
                          'results': []} 
        
        # loop through results in order to nest results in their respective test
        # entry instances (test_id)
        for _, test_result, result_type, _ in results:
                res = {'result_name': result_type.result_name, 
                        'result_value': test_result.result_value,
                        'evaluation': test_result.evaluation}
                nested_results['results'].append(res)

        payload = {}
        payload['items'] = [nested_results]
        payload['tests'] = 1
        payload['test_results'] = len( nested_results['results'])
        payload['user_id'] = results[0][0].user_id
        return payload

@ns.route('/bloodtest/results/all/<int:user_id>/')
@ns.doc(params={'user_id': 'Client ID number'})
class AllMedBloodTestResults(Resource):
    """
    Endpoint for returning all blood test results from a client
    """
    @token_auth.login_required
    @responds(schema=MedicalBloodTestResultsOutputSchema, api=ns)
    def get(self, user_id):
        # pull up all tests, test results, and the test type names for this client
        results =  db.session.query(
                        MedicalBloodTests, MedicalBloodTestResults, MedicalBloodTestResultTypes, User
                        ).join(
                            MedicalBloodTestResultTypes
                        ).join(MedicalBloodTests
                        ).filter(
                            MedicalBloodTests.test_id == MedicalBloodTestResults.test_id
                        ).filter(
                            MedicalBloodTests.user_id==user_id
                        ).filter(
                            MedicalBloodTests.reporter_id == User.user_id
                        ).all()

        test_ids = set([(x[0].test_id, x[0].reporter_id, x[3].firstname, x[3].lastname) for x in results])
        nested_results = [{'test_id': x[0], 'reporter_id': x[1], 'reporter_firstname': x[2], 'reporter_lastname': x[3], 'results': []} for x in test_ids ]
        
        # loop through results in order to nest results in their respective test
        # entry instances (test_id)
        for test_info, test_result, result_type, _ in results:
            for test in nested_results:
                # add rest result to appropriate test entry instance (test_id)
                if test_result.test_id == test['test_id']:
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
        payload['user_id'] = user_id
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

@ns.route('/medicalhistory/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedHistory(Resource):
    @token_auth.login_required
    @responds(schema=MedicalHistorySchema, api=ns)
    def get(self, user_id):
        """returns client's medical history as a json for the user_id specified"""
        check_client_existence(user_id)

        client = MedicalHistory.query.filter_by(user_id=user_id).first()

        if not client:
            raise ContentNotFound()

        return client

    @token_auth.login_required
    @accepts(schema=MedicalHistorySchema, api=ns)
    @responds(schema=MedicalHistorySchema, status_code=201, api=ns)
    def post(self, user_id):
        """returns client's medical history as a json for the user_id specified"""
        check_client_existence(user_id)

        current_med_history = MedicalHistory.query.filter_by(user_id=user_id).first()
        
        if current_med_history:
            raise IllegalSetting(message=f"Medical History for user_id {user_id} already exists. Please use PUT method")


        data = request.get_json()
        data["user_id"] = user_id

        mh_schema = MedicalHistorySchema()

        client_mh = mh_schema.load(data)

        db.session.add(client_mh)
        db.session.commit()

        return client_mh

    @token_auth.login_required
    @accepts(schema=MedicalHistorySchema, api=ns)
    @responds(schema=MedicalHistorySchema, api=ns)
    def put(self, user_id):
        """updates client's medical history as a json for the user_id specified"""
        check_client_existence(user_id)

        client_mh = MedicalHistory.query.filter_by(user_id=user_id).first()

        if not client_mh:
            raise UserNotFound(user_id, message = f"The client with id: {user_id} does not yet have a medical history in the database")
        
        # get payload and update the current instance followd by db commit
        data = request.get_json()
        
        data['last_examination_date'] = datetime.strptime(data['last_examination_date'], "%Y-%m-%d")
        
        # update resource 
        client_mh.update(data)

        db.session.commit()

        return client_mh


@ns.route('/physical/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedPhysical(Resource):
    @token_auth.login_required
    @responds(schema=MedicalPhysicalExamSchema(many=True), api=ns)
    def get(self, user_id):
        """returns all client's medical physical exams for the user_id specified"""
        check_client_existence(user_id)

        query =  db.session.query(
                MedicalPhysicalExam, User.firstname, User.lastname
                ).filter(
                    MedicalPhysicalExam.user_id == user_id
                ).filter(
                    MedicalPhysicalExam.reporter_id == User.user_id
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
    def post(self, user_id):
        """creates new db entry of client's medical physical exam as a json for the clientuser_idid specified"""
        check_client_existence(user_id)

        data = request.get_json()
        data["user_id"] = user_id

        client_mp = MedicalPhysicalExamSchema().load(data)

        # look up the reporting staff member and add their id to the 
        # client's physical entry
        reporter = token_auth.current_user()[0]
        client_mp.reporter_id = reporter.user_id

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

@ns.route('/medicalinstitutions/recordid/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ExternalMedicalRecordIDs(Resource):
    @token_auth.login_required
    @accepts(schema=ClientExternalMREntrySchema,  api=ns)
    @responds(schema=ClientExternalMREntrySchema,status_code=201, api=ns)
    def post(self, user_id):
        """for submitting client medical record ids from external medical institutions"""

        data = request.get_json()
        # check for new institute names. If the institute_id is 9999, then enter 
        # the new institute into the dabase before proceeding
        data_cleaned = []
        for record in data['record_locators']:
            record["user_id"] = user_id # add in the user_id
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
    def get(self, user_id):
        """returns all medical record ids for user_id"""

        client_med_record_ids = ClientExternalMR.query.filter_by(user_id=user_id).all()

        return client_med_record_ids


@ns.route('/surgery/')
class ClientSurgeriesAPI(Resource):

    @token_auth.login_required
    @accepts(schema=ClientSurgeriesSchema,  api=ns)
    @responds(schema=ClientSurgeriesSchema, status_code=201, api=ns)
    def post(self):
        """register a client surgery in the db"""
        #check client and reporting staff have valid user ids
        check_client_existence(request.parsed_obj['client_user_id'])
        check_staff_existence(request.parsed_obj['reporter_user_id'])

        #add request data to db
        surgery = ClientSurgeries().load(request.parsed_obj)
        db.session.add(surgery)
        db.session.commit()

        return surgery

    @token_auth.login_required
    @accepts(schema=JustUserIdSchema)
    @responds(schema=ClientSurgeriesSchema(many=True), api=ns)
    def get(self):
        """returns a list of all surgeries for the given client_user_id"""
        check_client_existence(request.parsed_obj['client_user_id'])
        return ClientSurgeries.query.filter_by(client_user_id=request.parsed_obj['client_user_id']).all()

##########################
# This code became obsolete, because the medical lookup tables is now
# provided by endpoint. But I'm keeping the code around because it might
# be useful in the future.
#
# def _generate_lut_endpoints(name, lut):
#     # Set up the GET method
#     @token_auth.login_required
#     @responds(status_code=200, api=ns)
#     def get(self):
#         return jsonify(lut)
#
#     # Normal docstring cannot be an f-string or use .format(), but this works.
#     get.__doc__ = f"""
#         Lookup table for supported medical conditions -- {name}.
#
#         Returns
#         -------
#         dict(dict(...))
#             Nested dicts, where the keys are the supported (category of)
#             medical issues. The values are either another dict to specify
#             a subdivision, or ``null`` indicating no further nesting.
#         """
#
#     # Create class based on name
#     endp = type(f'MedicalLUT{name}Endpoint', (Resource,), {'get': get})
#
#     # Add class as endpoint to namespace (instead of class decorator)
#     ns.add_resource(endp, f'/condition/{name}/')
#
#     return endp
#
# for name, lut in MEDICAL_CONDITIONS:
#     _generate_lut_endpoints(name, lut)
#
##########################

@ns.route('/conditions/')
class MedicalConditionsEndpoint(Resource):
    """ Lookup table for supported medical conditions. """

    @token_auth.login_required
    @responds(status_code=200, api=ns)
    def get(self):
        """ Lookup table for supported medical conditions.

        Returns
        -------
        dict(dict(...))
            Nested dict, where the keys are the supported (category of)
            medical issues. The values are either another dict to specify
            a subdivision, or ``null`` indicating no further nesting.
        """
        return jsonify(MEDICAL_CONDITIONS)
