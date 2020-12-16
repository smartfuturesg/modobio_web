import os, boto3, secrets, pathlib
from datetime import datetime
from dateutil.relativedelta import relativedelta

from flask import request, current_app, jsonify
from flask_accepts import accepts, responds
from flask_restx import Resource, Api

from odyssey import db
from odyssey.api.doctor.models import (
    MedicalLookUpSTD,
    MedicalFamilyHistory,
    MedicalConditions,
    MedicalPhysicalExam,
    MedicalGeneralInfo,
    MedicalGeneralInfoMedications,
    MedicalGeneralInfoMedicationAllergy,
    MedicalHistory, 
    MedicalBloodTests,
    MedicalBloodTestResults,
    MedicalBloodTestResultTypes, 
    MedicalImaging,
    MedicalExternalMR,
    MedicalSocialHistory,
    MedicalSTDHistory,
    MedicalSurgeries
)
from odyssey.api.facility.models import MedicalInstitutions
from odyssey.api.user.models import User
from odyssey.api import api
from odyssey.utils.auth import token_auth
from odyssey.utils.errors import (
    UserNotFound, 
    IllegalSetting, 
    ContentNotFound,
    InputError,
    MedicalConditionAlreadySubmitted
)
from odyssey.utils.misc import check_client_existence, check_staff_existence, check_blood_test_existence, check_blood_test_result_type_existence, check_user_existence, check_medical_condition_existence, check_std_existence
from odyssey.api.doctor.schemas import (
    AllMedicalBloodTestSchema,
    CheckBoxArrayDeleteSchema,
    MedicalFamilyHistSchema,
    MedicalFamilyHistInputSchema,
    MedicalFamilyHistOutputSchema,
    MedicalConditionsOutputSchema,
    MedicalConditionsSchema,
    MedicalGeneralInfoSchema,
    MedicalGeneralInfoInputSchema,
    MedicalAllergiesInfoInputSchema,
    MedicalMedicationsInfoInputSchema,
    MedicalHistorySchema, 
    MedicalPhysicalExamSchema, 
    MedicalInstitutionsSchema,
    MedicalBloodTestsInputSchema,
    MedicalBloodTestSchema,
    MedicalBloodTestResultsSchema,
    MedicalBloodTestResultsOutputSchema,
    MedicalBloodTestResultTypesSchema,
    MedicalImagingSchema,
    MedicalExternalMREntrySchema, 
    MedicalExternalMRSchema,
    MedicalSocialHistorySchema,
    MedicalLookUpSTDOutputSchema,
    MedicalSTDHistorySchema,
    MedicalSTDHistoryInputSchema,
    MedicalSocialHistoryOutputSchema,
    MedicalSurgeriesSchema
)
from odyssey.utils.constants import MEDICAL_CONDITIONS

ns = api.namespace('doctor', description='Operations related to doctor')

@ns.route('/medicalgeneralinfo/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedicalGenInformation(Resource):
    @token_auth.login_required
    @responds(schema=MedicalGeneralInfoInputSchema(exclude=['medications.idx','allergies.idx']), api=ns)
    def get(self, user_id):
        '''
        This request gets the users personal and family history if it exists
        '''
        check_client_existence(user_id)
        genInfo = MedicalGeneralInfo.query.filter_by(user_id=user_id).first()
        medications = MedicalGeneralInfoMedications.query.filter_by(user_id=user_id).all()
        allergies = MedicalGeneralInfoMedicationAllergy.query.filter_by(user_id=user_id).all()
        payload = {'gen_info': genInfo,
                   'medications': medications,
                   'allergies': allergies}
        return payload

    @token_auth.login_required
    @accepts(schema=MedicalGeneralInfoInputSchema(exclude=['medications.idx','allergies.idx']), api=ns)
    @responds(schema=MedicalGeneralInfoInputSchema(exclude=['medications.idx','allergies.idx']), status_code=201, api=ns)
    def post(self, user_id):
        '''
        Post request to post the client's onboarding personal and family history
        '''
        # First check if the client exists
        check_client_existence(user_id)
        payload = {}
        generalInfo = request.parsed_obj['gen_info']
        if generalInfo:

            genInfo = MedicalGeneralInfo.query.filter_by(user_id=user_id).one_or_none()
            if genInfo:
                db.session.delete(genInfo)

            if generalInfo.primary_doctor_contact_name:
                # If the client has a primary care doctor, we need either the 
                # phone number or email
                if not generalInfo.primary_doctor_contact_phone and \
                    not generalInfo.primary_doctor_contact_email:
                    db.session.rollback()
                    raise InputError(status_code = 405,message='If a primary doctor name is given, the client must also\
                                        provide the doctors phone number or email')      
            if generalInfo.blood_type or generalInfo.blood_type_positive is not None:
                # if the client starts by indication which blood type they have or the sign
                # they also need the other.
                if generalInfo.blood_type is None or generalInfo.blood_type_positive is None:
                    db.session.rollback()
                    raise InputError(status_code = 405,message='If bloodtype or sign is given, client must provide both.')
            generalInfo.user_id = user_id
            db.session.add(generalInfo)

            payload['gen_info'] = generalInfo

        if request.parsed_obj['medications']:
            medications = request.parsed_obj['medications']
            payload['medications'] = []
            # Before storing data, delete what exists in the database
            meds = MedicalGeneralInfoMedications.query.filter_by(user_id=user_id).all()
            for med in meds:
                db.session.delete(med)
            
            for medication in medications:
                # If the client is taking medications, they MUST tell us what
                # medication
                if medication.medication_name is None:
                    db.session.rollback()
                    raise InputError(status_code = 405, message='Medication Name Required')
                else:
                    # If the client gives a medication dosage, they must also give 
                    # the units
                    if medication.medication_dosage and medication.medication_units is None:
                        db.session.rollback()
                        raise InputError(status_code = 405,message='Medication dosage requires units')
                    if medication.medication_freq:
                        if medication.medication_times_per_freq is None and medication.medication_time_units is None:
                            db.session.rollback()
                            raise InputError(status_code = 405,message='Medication frequency needs more information')
                    medication.user_id = user_id
                    db.session.add(medication)

                    payload['medications'].append(medication)
            

        # If the client is allergic to certain medication, they MUST tell us what
        # medication
        if request.parsed_obj['allergies']:
            allergies = request.parsed_obj['allergies']
            payload['allergies'] = []
            
            allergiesInDB = MedicalGeneralInfoMedicationAllergy.query.filter_by(user_id=user_id).all()
            for allergy in allergiesInDB:
                db.session.delete(allergy)

            for allergicTo in allergies:
                if not allergicTo.medication_name:
                    # If the client indicates they have an allergy to a medication
                    # they must AT LEAST send the name of the medication they are allergic to
                    db.session.rollback()
                    raise InputError(status_code = 405,message='Must need the name of the medication client is allergic to.')
                else:
                    allergicTo.user_id = user_id
                    payload['allergies'].append(allergicTo)
                    db.session.add(allergicTo)      

        # insert results into the result table
        db.session.commit()
        return payload


@ns.route('/medicalinfo/general/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedicalGeneralInformation(Resource):
    @token_auth.login_required
    @responds(schema=MedicalGeneralInfoSchema, api=ns)
    def get(self, user_id):
        '''
        This request gets the users personal and family history if it exists
        '''
        check_client_existence(user_id)
        genInfo = MedicalGeneralInfo.query.filter_by(user_id=user_id).first()
        payload = {'general_info': genInfo}
        return genInfo

    @token_auth.login_required
    @accepts(schema=MedicalGeneralInfoSchema, api=ns)
    @responds(schema=MedicalGeneralInfoSchema, status_code=201, api=ns)
    def post(self, user_id):
        '''
        Post request to post the client's onboarding personal and family history
        '''
        # First check if the client exists
        check_client_existence(user_id)
        
        genInfo = MedicalGeneralInfo.query.filter_by(user_id=user_id).one_or_none()
        if genInfo:
            raise InputError(status_code=405,message='Please use put request.')

        generalInfo = request.parsed_obj
        if generalInfo:
            if generalInfo.primary_doctor_contact_name:
                # If the client has a primary care doctor, we need either the 
                # phone number or email
                if not generalInfo.primary_doctor_contact_phone and \
                    not generalInfo.primary_doctor_contact_email:
                    raise InputError(status_code = 405,message='If a primary doctor name is given, the client must also\
                                        provide the doctors phone number or email')      
            
            if generalInfo.blood_type or generalInfo.blood_type_positive:
                # if the client starts by indication which blood type they have or the sign
                # they also need the other.
                if generalInfo.blood_type is None or generalInfo.blood_type_positive is None:
                    raise InputError(status_code = 405,message='If bloodtype or sign is given, client must provide both.')
                else:
                    generalInfo.user_id = user_id
            db.session.add(generalInfo)
        else:
            # If first post is empty, put in a placeholder in this table to force to use
            # a put request
            generalInfo.user_id = user_id
            db.session.add(generalInfo)     
        # insert results into the result table
        db.session.commit()
        return generalInfo

    @token_auth.login_required
    @accepts(schema=MedicalGeneralInfoSchema, api=ns)
    @responds(schema=MedicalGeneralInfoSchema, status_code=201, api=ns)
    def put(self, user_id):
        '''
        Put request to update the client's onboarding personal and family history
        '''
        check_client_existence(user_id)

        generalInfo = request.parsed_obj
        if generalInfo:
            del generalInfo.__dict__['_sa_instance_state']
            if generalInfo.primary_doctor_contact_name:
                # If the client has a primary care doctor, we need either the 
                # phone number or email
                if not generalInfo.primary_doctor_contact_phone and \
                    not generalInfo.primary_doctor_contact_email:
                    raise InputError(status_code = 405,message='If a primary doctor name is given, the client must also\
                                        provide the doctors phone number or email')      
            if generalInfo.blood_type or generalInfo.blood_type_positive:
                # if the client starts by indication which blood type they have or the sign
                # they also need the other.
                if generalInfo.blood_type is None or generalInfo.blood_type_positive is None:
                    raise InputError(status_code = 405,message='If bloodtype or sign is given, client must provide both.')
                else:
                    generalInfo.__dict__['user_id'] = user_id
            genInfo = MedicalGeneralInfo.query.filter_by(user_id=user_id).one_or_none()
            genInfo.update(generalInfo.__dict__)
        
        # insert results into the result table
        db.session.commit()
        return generalInfo

@ns.route('/medicalinfo/medications/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedicalMedicationInformation(Resource):
    @token_auth.login_required
    @responds(schema=MedicalMedicationsInfoInputSchema, api=ns)
    def get(self, user_id):
        '''
        This request gets the users personal and family history if it exists
        '''
        check_client_existence(user_id)
        medications = MedicalGeneralInfoMedications.query.filter_by(user_id=user_id).all()
        payload = {'medications': medications}
        return payload

    @token_auth.login_required
    @accepts(schema=MedicalMedicationsInfoInputSchema(exclude=['medications.idx']), api=ns)
    @responds(schema=MedicalMedicationsInfoInputSchema, status_code=201, api=ns)
    def post(self, user_id):
        '''
        Post request to post the client's onboarding personal and family history
        '''
        # First check if the client exists
        check_client_existence(user_id)
        
        payload = {}

        if request.parsed_obj['medications']:
            medications = request.parsed_obj['medications']
            payload['medications'] = []

            for medication in medications:
                # If the client is taking medications, they MUST tell us what
                # medication
                if not medication.medication_name:
                    raise InputError(status_code = 405, message='Medication Name Required')
                else:
                    # If the client gives a medication dosage, they must also give 
                    # the units
                    if medication.medication_dosage and not medication.medication_units:
                        raise InputError(status_code = 405,message='Medication dosage requires units')
                    if medication.medication_freq:
                        if not medication.medication_times_per_freq and not medication.medication_time_units:
                            raise InputError(status_code = 405,message='Medication frequency needs more information')
                    medication.user_id = user_id
                    payload['medications'].append(medication)
                    db.session.add(medication)    
        
        # insert results into the result table
        db.session.commit()
        return payload

    @token_auth.login_required
    @accepts(schema=MedicalMedicationsInfoInputSchema, api=ns)
    @responds(schema=MedicalMedicationsInfoInputSchema, status_code=201, api=ns)
    def put(self, user_id):
        '''
        Put request to update the client's onboarding personal and family history
        '''
        payload = {}

        check_client_existence(user_id)

        if request.parsed_obj['medications']:
            medications = request.parsed_obj['medications']
            payload['medications'] = []
            for medication in medications:
                # If the client is taking medications, they MUST tell us what
                # medication
                if not medication.medication_name:
                    raise InputError(status_code = 405, message='Medication Name Required')
                else:
                    # If the client gives a medication dosage, they must also give 
                    # the units
                    if medication.medication_dosage and not medication.medication_units:
                        raise InputError(status_code = 405,message='Medication dosage requires units')
                    if medication.medication_freq:
                        if not medication.medication_times_per_freq and not medication.medication_time_units:
                            raise InputError(status_code = 405,message='Medication frequency needs more information')
                    medication.__dict__['user_id'] = user_id
                    # If medication and user are in it already, then send an update
                    # else, add it to the db
                    medicationInDB = MedicalGeneralInfoMedications.query.filter_by(user_id=user_id).filter_by(idx=medication.idx).one_or_none()
                    if medicationInDB:
                        del medication.__dict__['_sa_instance_state']
                        medicationInDB.update(medication.__dict__)
                    
                    payload['medications'].append(medication)
        
        # insert results into the result table
        db.session.commit()
        return payload        

    @token_auth.login_required
    @accepts(schema=CheckBoxArrayDeleteSchema, api=ns)
    @responds(status_code=201, api=ns)
    def delete(self, user_id):
        '''
        Put request to update the client's onboarding personal and family history
        '''
        payload = {}

        check_client_existence(user_id)
        
        ids_to_delete = request.parsed_obj['delete_ids']
        for ids in ids_to_delete:
            medicationInDB = MedicalGeneralInfoMedications.query.filter_by(user_id=user_id).filter_by(idx=ids['idx']).one_or_none()
            if medicationInDB:
                db.session.delete(medicationInDB)
        
        # insert results into the result table
        db.session.commit()
        return 201        


@ns.route('/medicalinfo/allergies/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedicalAllergiesInformation(Resource):
    @token_auth.login_required
    @responds(schema=MedicalAllergiesInfoInputSchema, api=ns)
    def get(self, user_id):
        '''
        This request gets the users personal and family history if it exists
        '''
        check_client_existence(user_id)
        allergies = MedicalGeneralInfoMedicationAllergy.query.filter_by(user_id=user_id).all()
        payload = {'allergies': allergies}
        return payload

    @token_auth.login_required
    @accepts(schema=MedicalAllergiesInfoInputSchema(exclude=['allergies.idx']), api=ns)
    @responds(schema=MedicalAllergiesInfoInputSchema, status_code=201, api=ns)
    def post(self, user_id):
        '''
        Post request to post the client's onboarding personal and family history
        '''
        # First check if the client exists
        check_client_existence(user_id)
        
        payload = {}

        # If the client is allergic to certain medication, they MUST tell us what
        # medication   
        if request.parsed_obj['allergies']:
            allergies = request.parsed_obj['allergies']
            payload['allergies'] = []
            for allergicTo in allergies:
                if not allergicTo.medication_name:
                    # If the client indicates they have an allergy to a medication
                    # they must AT LEAST send the name of the medication they are allergic to
                    raise InputError(status_code = 405,message='Must need the name of the medication client is allergic to.')
                else:
                    allergicTo.user_id = user_id
                    payload['allergies'].append(allergicTo)
                    db.session.add(allergicTo)      
        
        # insert results into the result table
        db.session.commit()
        return payload

    @token_auth.login_required
    @accepts(schema=MedicalAllergiesInfoInputSchema, api=ns)
    @responds(schema=MedicalAllergiesInfoInputSchema, status_code=201, api=ns)
    def put(self, user_id):
        '''
        Put request to update the client's onboarding personal and family history
        '''
        payload = {}

        check_client_existence(user_id)

        # If the client is allergic to certain medication, they MUST tell us what
        # medication
        if request.parsed_obj['allergies']:
            allergies = request.parsed_obj['allergies']
            payload['allergies'] = []
            for allergicTo in allergies:
                if not allergicTo.medication_name:
                    # If the client indicates they have an allergy to a medication
                    # they must AT LEAST send the name of the medication they are allergic to
                    raise InputError(status_code = 405,message='Must need the name of the medication client is allergic to.')
                else:
                    allergicTo.__dict__['user_id'] = user_id
                    allergyInDB = MedicalGeneralInfoMedicationAllergy.query.filter_by(user_id=user_id).filter_by(idx=allergicTo.idx).one_or_none() 
                    if allergyInDB:
                        del allergicTo.__dict__['_sa_instance_state']
                        allergyInDB.update(allergicTo.__dict__)
                    else:
                        db.session.add(allergicTo)
                    payload['allergies'].append(allergicTo)
        
        # insert results into the result table
        db.session.commit()
        return payload

    @token_auth.login_required
    @accepts(schema=CheckBoxArrayDeleteSchema, api=ns)
    @responds(status_code=201, api=ns)
    def delete(self, user_id):
        '''
        delete request to update the client's onboarding personal and family history
        '''

        check_client_existence(user_id)
        
        # If the client is allergic to certain medication, they MUST tell us what
        # medication

        ids_to_delete = request.parsed_obj['delete_ids']
        for ids in ids_to_delete:
            allergyInDB = MedicalGeneralInfoMedicationAllergy.query.filter_by(user_id=user_id).filter_by(idx=ids['idx']).one_or_none()
            if allergyInDB:
                db.session.delete(allergyInDB)
        
        # insert results into the result table
        db.session.commit()
        return 

@ns.route('/lookupstd/')
class MedicalLookUpSTDResource(Resource):
    """ Returns STD list stored in the database in response to a GET request.

    Returns
    -------
    dict
        JSON encoded dict.
    """
    @token_auth.login_required
    @responds(schema=MedicalLookUpSTDOutputSchema,status_code=200, api=ns)
    def get(self):
        std_types = MedicalLookUpSTD.query.all()
        payload = {'items': std_types,
                   'total_items': len(std_types)}

        return payload

@ns.route('/medicalinfo/std/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedicalSTDHist(Resource):
    @token_auth.login_required
    @accepts(schema=MedicalSTDHistoryInputSchema, api=ns)
    @responds(schema=MedicalSTDHistoryInputSchema, status_code=201, api=ns)
    def post(self, user_id):
        """ Submit STD History for client ``user_id`` in response to a PUT request.

        This endpoint submits or updates a client's STD history. 

        Example payload:
        {
            "stds": [
                {"std_id": int},
                {"std_id": int}

            ]
        }

        ***std_id is the STD id from the STDLookUp table in the database and can be retrieved
        from the endpoint /doctor/lookupstd/

        Parameters
        ----------
        user_id : int
            User ID number.

        Returns
        -------
        dict
            JSON encoded dict.
        """
        # First check if the client exists
        check_client_existence(user_id)
        # the data expected for the backend is:
        # parameter: user_id 
        stds = request.parsed_obj['stds']
        for std in stds:
            check_std_existence(std.std_id)
            user_and_std = MedicalSTDHistory.query.filter_by(user_id=user_id).filter_by(std_id=std.std_id).one_or_none()
            # If the payload contains an STD for a user already, then just continue
            if user_and_std:
                continue
            else:
                std.user_id = user_id
                db.session.add(std)
        payload = {'stds': stds}
        
        # insert results into the result table
        db.session.commit()
        return payload

    @token_auth.login_required
    @accepts(schema=MedicalSTDHistoryInputSchema, api=ns)
    @responds(status_code=201, api=ns)
    def delete(self, user_id):
        """ Delete STD History for client ``user_id`` in response to a delete request.

        This endpoint deletes a client's STD history. 

        Example payload:
        {
            "stds": [
                {"std_id": int},
                {"std_id": int}
            ]
        }

        ***std_id is the STD id from the STDLookUp table in the database and can be retrieved
        from the endpoint /doctor/lookupstd/

        Parameters
        ----------
        user_id : int
            User ID number.

        Returns
        -------
        dict
            JSON encoded dict.
        """
        stds = request.parsed_obj['stds']
        for std in stds:
            check_std_existence(std.std_id)
            user_and_std = MedicalSTDHistory.query.filter_by(user_id=user_id).filter_by(std_id=std.std_id).one_or_none()
            # If the payload contains an STD for a user already, then just continue
            if user_and_std:
                db.session.delete(user_and_std)
        
        # insert results into the result table
        db.session.commit()
        return 201

@ns.route('/medicalinfo/social/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedicalSocialHist(Resource):
    @token_auth.login_required
    @responds(schema=MedicalSocialHistoryOutputSchema, api=ns)
    def get(self, user_id):
        """ This request retrieves the social history
        for client ``user_id`` in response to a GET request.

        The example returned payload will look like 
        {
            "social_history": {
                "currently_smoke": bool,
                "avg_num_cigs": int,
                "num_years_smoked": int,
                "last_smoke": int,
                "last_smoke_time": str,
                "plan_to_stop": bool,
                "avg_weekly_drinks": int,
                "avg_weekly_workouts": int,
                "job_title": str,
                "avg_hourly_meditation": int,
                "sexual_preference": str
            }
            "std_history": [
                {"std_id": int},
                {"std_id: int}
            ]
        }

        Parameters
        ----------
        user_id : int
            User ID number.

        Returns
        -------
        dict
            JSON encoded dict.
        """
        check_client_existence(user_id)
        social_hist = MedicalSocialHistory.query.filter_by(user_id=user_id).one_or_none()
        std_hist = MedicalSTDHistory.query.filter_by(user_id=user_id).all()
        payload = {'social_history': social_hist,
                   'std_history': std_hist}
        return payload

    @token_auth.login_required
    @accepts(schema=MedicalSocialHistorySchema, api=ns)
    @responds(schema=MedicalSocialHistorySchema, status_code=201, api=ns)
    def post(self, user_id):
        """ This request submits the social history
        for client ``user_id`` in response to a POST request.

        The example returned payload will look like 
        {
            "currently_smoke": bool,
            "avg_num_cigs": int,
            "num_years_smoked": int,
            "last_smoke": int,
            "last_smoke_time": str,
            "plan_to_stop": bool,
            "avg_weekly_drinks": int,
            "avg_weekly_workouts": int,
            "job_title": str,
            "avg_hourly_meditation": int,
            "sexual_preference": str
        }

        Parameters
        ----------
        user_id : int
            User ID number.

        Returns
        -------
        dict
            JSON encoded dict.
        """
        # First check if the client exists
        check_client_existence(user_id)
        # Check if this information is already in the DB
        socialHist = MedicalSocialHistory.query.filter_by(user_id=user_id).one_or_none()
        data = request.parsed_obj
        payload = request.get_json()
        if socialHist:
            raise InputError(status=405,message='Social History has already been posted, please use put request.')
        # if currently smoke is false
        if not data.currently_smoke:
            # if last smoke or last smoke time (months/years)
            # is present, then both must be present
            if payload['last_smoke'] or payload['last_smoke_time']:
                if payload['last_smoke'] is None or payload['last_smoke_time'] is None: 
                    raise InputError(status=405, message='User must include when they last smoked, and include the time frame months or years.')
                
                if(payload['last_smoke_time'] == 'days'):
                    data.__dict__['last_smoke_date'] = datetime.now() - relativedelta(months=payload['last_smoke'])                
                elif(payload['last_smoke_time'] == 'months'):
                    data.__dict__['last_smoke_date'] = datetime.now() - relativedelta(months=payload['last_smoke'])
                elif(payload['last_smoke_time'] == 'years'):
                    data.__dict__['last_smoke_date'] = datetime.now() - relativedelta(years=payload['last_smoke'])
        data.__dict__['user_id'] = user_id
        db.session.add(data)
        # insert results into the result table
        db.session.commit()
        return data

    @token_auth.login_required
    @accepts(schema=MedicalSocialHistorySchema, api=ns)
    @responds(schema=MedicalSocialHistorySchema, status_code=201, api=ns)
    def put(self, user_id):
        """ This request updates the social history
        for client ``user_id`` in response to a PUT request.

        The example returned payload will look like 
        {
            "currently_smoke": bool,
            "avg_num_cigs": int,
            "num_years_smoked": int,
            "last_smoke": int,
            "last_smoke_time": str,
            "plan_to_stop": bool,
            "avg_weekly_drinks": int,
            "avg_weekly_workouts": int,
            "job_title": str,
            "avg_hourly_meditation": int,
            "sexual_preference": str
        }

        Parameters
        ----------
        user_id : int
            User ID number.

        Returns
        -------
        dict
            JSON encoded dict.
        """
        # First check if the client exists
        check_client_existence(user_id)
        # if currently smoke is false
        data = request.parsed_obj
        payload = request.get_json()

        if not data.currently_smoke:
            # if last smoke or last smoke time (months/years)
            # is present, then both must be present
            if payload['last_smoke'] or payload['last_smoke_time']:
                if payload['last_smoke'] is None or payload['last_smoke_time'] is None: 
                        raise InputError(status=405, message='User must include when they last smoked, and include the time frame months or years.')
                
                if(payload['last_smoke_time'] == 'days'):
                    data.__dict__['last_smoke_date'] = datetime.now() - relativedelta(months=payload['last_smoke'])                
                elif(payload['last_smoke_time'] == 'months'):
                    data.__dict__['last_smoke_date'] = datetime.now() - relativedelta(months=payload['last_smoke'])
                elif(payload['last_smoke_time'] == 'years'):
                    data.__dict__['last_smoke_date'] = datetime.now() - relativedelta(years=payload['last_smoke'])

        socialHist = MedicalSocialHistory.query.filter_by(user_id=user_id).one_or_none()
        
        del data.__dict__['_sa_instance_state']
        
        socialHist.update(data.__dict__)
        # insert results into the result table
        db.session.commit()
        return data    

@ns.route('/medicalconditions/')
class MedicalCondition(Resource):
    """
    Returns the medical conditions currently documented in the DB
    """
    @token_auth.login_required
    @responds(schema=MedicalConditionsOutputSchema,status_code=200, api=ns)
    def get(self):
        medcon_types = MedicalConditions.query.all()
        payload = {'items': medcon_types,
                   'total_items': len(medcon_types)}

        return payload

@ns.route('/familyhistory/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedicalFamilyHist(Resource):
    @token_auth.login_required
    @responds(schema=MedicalFamilyHistOutputSchema, api=ns)
    def get(self, user_id):
        '''
        This request gets the users personal and family history if it exists
        '''
        check_client_existence(user_id)
        client_personalfamilyhist = MedicalFamilyHistory.query.filter_by(user_id=user_id).all()
        payload = {'items': client_personalfamilyhist,
                   'total_items': len(client_personalfamilyhist)}
        return payload

    @token_auth.login_required
    @accepts(schema=MedicalFamilyHistInputSchema, api=ns)
    @responds(schema=MedicalFamilyHistOutputSchema, status_code=201, api=ns)
    def post(self, user_id):
        '''
        Post request to post the client's onboarding personal and family history
        '''
        # First check if the client exists
        check_client_existence(user_id)
        
        # the data expected for the backend is:
        # parameter: user_id 
        # payload: medical_condition_id, myself, father, mother, brother, sister

        for result in request.parsed_obj['conditions']:
            check_medical_condition_existence(result.medical_condition_id)
            user_and_medcon = MedicalFamilyHistory.query.filter_by(user_id=user_id).filter_by(medical_condition_id=result.medical_condition_id).one_or_none()
            if user_and_medcon:
                raise MedicalConditionAlreadySubmitted(user_id,result.medical_condition_id)
            result.user_id = user_id
            db.session.add(result)
        payload = {'items': request.parsed_obj['conditions'],
                   'total_items': len(request.parsed_obj['conditions'])}
        # insert results into the result table
        db.session.commit()
        return payload

    @token_auth.login_required
    @accepts(schema=MedicalFamilyHistInputSchema, api=ns)
    @responds(schema=MedicalFamilyHistOutputSchema, status_code=201, api=ns)
    def put(self, user_id):
        '''
        Put request to update the client's onboarding personal and family history
        '''
        # First check if the client exists
        check_client_existence(user_id)
        
        # the data expected for the backend is:
        # parameter: user_id 
        # payload: medical_condition_id, myself, father, mother, brother, sister

        for result in request.parsed_obj['conditions']:
            check_medical_condition_existence(result.medical_condition_id)
            user_and_medcon = MedicalFamilyHistory.query.filter_by(user_id=user_id).filter_by(medical_condition_id=result.medical_condition_id).one_or_none()
            
            if user_and_medcon:
                # raise ContentNotFound()
                del result.__dict__['_sa_instance_state']
                user_and_medcon.update(result.__dict__)
            else:
                result.user_id = user_id
                db.session.add(result)
        payload = {'items': request.parsed_obj['conditions'],
                   'total_items': len(request.parsed_obj['conditions'])}        
        # insert results into the result table
        db.session.commit()
        return payload

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
                if img.get('image_path'):
                    params['Key'] = img.get('image_path')
                    url = s3.generate_presigned_url('get_object', Params=params, ExpiresIn=3600)
                    img['image_path'] = url
 
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
    @accepts(schema=MedicalExternalMREntrySchema,  api=ns)
    @responds(schema=MedicalExternalMREntrySchema,status_code=201, api=ns)
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
            
        client_med_record_ids = MedicalExternalMRSchema(many=True).load(data_cleaned)
        
        db.session.add_all(client_med_record_ids)
        db.session.commit()
        
        return client_med_record_ids

    @token_auth.login_required
    @responds(schema=MedicalExternalMREntrySchema, api=ns)
    def get(self, user_id):
        """returns all medical record ids for user_id"""

        client_med_record_ids = MedicalExternalMR.query.filter_by(user_id=user_id).all()

        return client_med_record_ids


@ns.route('/surgery/<int:client_user_id>/')
@ns.doc(params={'client_user_id': 'Client user ID number'})
class MedicalSurgeriesAPI(Resource):

    @token_auth.login_required(user_type=('staff',))
    @accepts(schema=MedicalSurgeriesSchema,  api=ns)
    @responds(schema=MedicalSurgeriesSchema, status_code=201, api=ns)
    def post(self, client_user_id):
        """register a client surgery in the db"""
        #check client and reporting staff have valid user ids
        check_client_existence(client_user_id)

        #add request data to db
        request.parsed_obj.client_user_id = client_user_id
        request.parsed_obj.reporter_user_id = token_auth.current_user()[0].user_id
        db.session.add(request.parsed_obj)
        db.session.commit()

        return request.parsed_obj

    @token_auth.login_required
    @responds(schema=MedicalSurgeriesSchema(many=True), api=ns)
    def get(self, client_user_id):
        """returns a list of all surgeries for the given client_user_id"""
        check_client_existence(client_user_id)
        return MedicalSurgeries.query.filter_by(client_user_id=client_user_id).all()

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
