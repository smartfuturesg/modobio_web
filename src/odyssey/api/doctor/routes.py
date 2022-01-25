import logging

from odyssey.api.lookup.models import LookupBloodTests, LookupBloodTestRanges, LookupRaces
logger = logging.getLogger(__name__)

import os, boto3, secrets, pathlib

from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from flask import g, request, current_app
from flask_accepts import accepts, responds
from flask_restx import Resource, Namespace
from sqlalchemy import select
from werkzeug.exceptions import BadRequest, Unauthorized

from odyssey import db
from odyssey.api.doctor.models import (
    MedicalLookUpBloodPressureRange,
    MedicalLookUpSTD,
    MedicalFamilyHistory,
    MedicalConditions,
    MedicalPhysicalExam,
    MedicalGeneralInfo,
    MedicalGeneralInfoMedications,
    MedicalGeneralInfoMedicationAllergy,
    MedicalHistory,
    MedicalBloodPressures,
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
from odyssey.utils.auth import token_auth
from odyssey.utils.misc import (
    check_client_existence,
    check_blood_test_existence,
    check_blood_test_result_type_existence,
    check_medical_condition_existence,
)
from odyssey.utils.file_handling import FileHandling
from odyssey.utils.constants import IMAGE_MAX_SIZE, MED_ALLOWED_IMAGE_TYPES, BLOOD_TEST_IMAGE_MAX_SIZE
from odyssey.api.doctor.schemas import (
    AllMedicalBloodTestSchema,
    CheckBoxArrayDeleteSchema,
    MedicalBloodPressuresSchema,
    MedicalBloodPressuresOutputSchema,
    MedicalCredentialsSchema,
    MedicalCredentialsInputSchema,
    MedicalFamilyHistInputSchema,
    MedicalFamilyHistOutputSchema,
    MedicalConditionsOutputSchema,
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
    MedicalLookUpSTDOutputSchema,
    MedicalLookUpBloodPressureRangesOutputSchema,
    MedicalSocialHistoryOutputSchema,
    MedicalSurgeriesSchema
)
from odyssey.api.client.models import ClientFertility, ClientRaceAndEthnicity
from odyssey.api.staff.models import StaffRoles
from odyssey.api.practitioner.models import PractitionerCredentials
from odyssey.utils.base.resources import BaseResource

ns = Namespace('doctor', description='Operations related to doctor')

@ns.route('/credentials/<int:user_id>/')
class MedCredentials(BaseResource):
    @token_auth.login_required(user_type=('modobio',))
    @responds(schema=MedicalCredentialsInputSchema,status_code=200,api=ns)
    def get(self, user_id):
        """
        GET Request for Pulling Medical Credentials for a practitioner

        User should be Staff Self and community manager
        """

        #user_id = request.args.get('user_id',type=int)
        if not user_id:
            raise BadRequest('Missing User ID.')

        current_user, _ = token_auth.current_user()

        if current_user.is_staff:
            staff_user_roles = db.session.query(StaffRoles.role).filter(StaffRoles.user_id==current_user.user_id).all()
            staff_user_roles = [x[0] for x in staff_user_roles]            
            if current_user.user_id != user_id and 'community_manager' not in staff_user_roles:
                raise Unauthorized()

        query = db.session.execute(
            select(PractitionerCredentials).
            where(
                PractitionerCredentials.user_id == user_id
                )
        ).scalars().all()
        return {'items': query}

    @token_auth.login_required(user_type=('staff',),staff_role=('medical_doctor',))
    @accepts(schema=MedicalCredentialsInputSchema, api=ns)
    @responds(status_code=201,api=ns)
    def post(self, user_id):
        """
        POST Request for submitting Medical Credentials for a practitioner

        User should be Staff Self
        """

        #user_id = request.args.get('user_id',type=int)
        if not user_id:
            raise BadRequest('Missing User ID.')
        

        curr_credentials = PractitionerCredentials.query.filter_by(user_id=user_id).all()     
        verified_cred = []
        if curr_credentials:
            for curr_cred in curr_credentials:
                if curr_cred.status != 'Verified':
                    db.session.delete(curr_cred)
                else:
                    verified_cred.append(curr_cred)
        
        payload = request.parsed_obj
        curr_role = StaffRoles.query.filter_by(user_id=user_id,role='medical_doctor').one_or_none()
        state_check = {}
        for cred in payload['items']:

            # This takes care of only allowing 1 state input per credential type
            # Example:
            # (Good) DEA - AZ, CA
            # (Bad)  DEA - AZ, AZ
            if cred.credential_type not in state_check:
                state_check[cred.credential_type]=[]
                state_check[cred.credential_type].append(cred.state)
            else:
                if cred.state in state_check[cred.credential_type]:
                    # Rollback is necessary because we applied database changes above
                    db.session.rollback()
                    raise BadRequest(f'Multiple {cred.state} submissions for {cred.credential_type}. '
                                     f'Only one credential per state is allowed')
                else:
                    state_check[cred.credential_type].append(cred.state)

            # These are already verified, however if for SOME reason
            # A Medical Doctor wants to update their credentials,
            # We will update that credential and reset the status from Verified to Pending Verification
            if verified_cred:
                for curr_cred in verified_cred:
                    cred_exists = False
                    if cred.credential_type == curr_cred.credential_type:
                        if cred.country_id == curr_cred.country_id and \
                            cred.state == curr_cred.state:
                                if cred.credentials != curr_cred.credentials:
                                    # We update the medical doctor's credentials
                                    # and we reset the status from Verified -> Pending Verification
                                    curr_cred.update({'credentials': cred.credentials,'status':'Pending Verification'})
                                cred_exists = True
                                break
                if not cred_exists:
                    cred.status = 'Pending Verification'
                    cred.role_id = curr_role.idx
                    cred.user_id = user_id
                    db.session.add(cred)
            else:
                cred.status = 'Pending Verification' if not any([current_app.config['DEV'],current_app.config['TESTING']]) else 'Verified'
                cred.role_id = curr_role.idx
                cred.user_id = user_id
                db.session.add(cred)
        db.session.commit()
        return 

    @token_auth.login_required(staff_role=('community_manager',))
    @accepts(schema=MedicalCredentialsSchema(only=['idx','status']),api=ns)
    @responds(status_code=201,api=ns)
    def put(self, user_id):
        """
        PUT Request for updating the status for medical credentials

        User for this request should be the Staff Admin
        """

        payload = request.json
        #user_id = request.args.get('user_id',type=int)
        if not user_id:
            raise BadRequest('Missing User ID.')
        
        status = ['Verified','Pending Verification', 'Rejected']
        if payload['status'] not in status:
            raise BadRequest('Status must be one of {}.'.format(', '.join(status)))

        curr_credentials = PractitionerCredentials.query.filter_by(user_id=user_id,idx=payload['idx']).one_or_none()

        if curr_credentials:
            curr_credentials.update(payload)
            db.session.commit()
        else:
            raise BadRequest('Credentials not found.')
        return

    @token_auth.login_required(staff_role=('medical_doctor','community_manager'))
    @accepts(schema=MedicalCredentialsSchema(exclude=('status','credential_type','expiration_date','state','want_to_practice','credentials','country_id')),api=ns)
    @responds(status_code=201,api=ns)
    def delete(self, user_id):
        """
        DELETE Request for deleting medical credentials

        User for this request should be the Staff Self and Staff Admin
        """
        #user_id = request.args.get('user_id',type=int)
        if not user_id:
            raise BadRequest('Missing User ID.')
                
        current_user, _ = token_auth.current_user()
        staff_user_roles = db.session.query(StaffRoles.role).filter(StaffRoles.user_id==current_user.user_id).all()
        staff_user_roles = [x[0] for x in staff_user_roles]
        
        if current_user.user_id != user_id and 'community_manager' not in staff_user_roles:
            raise Unauthorized

        payload = request.json

        curr_credentials = PractitionerCredentials.query.filter_by(user_id=user_id,idx=payload['idx']).one_or_none()

        if curr_credentials:
            db.session.delete(curr_credentials)
            db.session.commit()
        else:
            raise BadRequest('Credentials not found.')
        return

@ns.route('/bloodpressure/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedBloodPressures(BaseResource):
    # Multiple blood pressure measurements per user allowed
    __check_resource__ = False

    @token_auth.login_required(resources=('blood_pressure',))
    @responds(schema=MedicalBloodPressuresOutputSchema, api=ns)
    def get(self, user_id):
        '''
        This request gets the users submitted blood pressure if it exists
        '''
        self.check_user(user_id, user_type='client')
        bp_info = MedicalBloodPressures.query.filter_by(user_id=user_id).all()
        
        for data in bp_info:
            reporter = User.query.filter_by(user_id=data.reporter_id).one_or_none()
            data.reporter_firstname = reporter.firstname
            data.reporter_lastname = reporter.lastname

        payload = {'items': bp_info,
                   'total_items': len(bp_info)}
        return payload

    @token_auth.login_required(staff_role=('medical_doctor',), resources=('blood_pressure',))
    @accepts(schema=MedicalBloodPressuresSchema, api=ns)
    @responds(schema=MedicalBloodPressuresSchema, status_code=201, api=ns)
    def post(self, user_id):
        '''
        Post request to post the client's blood pressure
        '''
        # First check if the client exists
        self.check_user(user_id, user_type='client')
        self.set_reporter_id(request.parsed_obj)

        request.parsed_obj.user_id = user_id
        
        db.session.add(request.parsed_obj)
        db.session.commit()

        return request.parsed_obj

    @token_auth.login_required(user_type=('client', 'staff'), staff_role=('medical_doctor',), resources=('blood_pressure',))
    @ns.doc(params={'idx': 'int',})
    @responds(status_code=204, api=ns)
    def delete(self, user_id):
        '''
        Delete request for a client's blood pressure
        '''
        self.check_user(user_id, user_type='client')

        idx = request.args.get('idx', type=int)
        if idx:
            result = MedicalBloodPressures.query.filter_by(user_id=user_id, idx=idx).one_or_none()
            if not result:
                raise BadRequest(f'Blood pressure result {idx} not found.')

            #ensure logged in user is the reporter for this pressure reasing
            self.check_ehr_permissions(result)

            db.session.delete(result)
            db.session.commit()
        else:
            raise BadRequest('idx must be an integer.')

@ns.route('/lookupbloodpressureranges/')
class MedicalLookUpBloodPressureResource(BaseResource):
    """ Returns blood pressure ranges stored in the database in response to a GET request.

    Returns
    -------
    dict
        JSON encoded dict.
    """
    @token_auth.login_required
    @responds(schema=MedicalLookUpBloodPressureRangesOutputSchema,status_code=200, api=ns)
    def get(self):
        bp_ranges = MedicalLookUpBloodPressureRange.query.all()
        payload = {'items': bp_ranges,
                   'total_items': len(bp_ranges)}

        return payload

@ns.route('/medicalgeneralinfo/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedicalGenInformation(BaseResource):
    @token_auth.login_required(resources=('medications', 'general_medical_info'))
    @responds(schema=MedicalGeneralInfoInputSchema(exclude=['medications.idx','allergies.idx']), api=ns)
    def get(self, user_id):
        '''
        This request gets the users personal and family history if it exists
        '''
        self.check_user(user_id, user_type='client')
        current_user, _ = token_auth.current_user()
        
        genInfo = MedicalGeneralInfo.query.filter_by(user_id=user_id).first()
        medications = MedicalGeneralInfoMedications.query.filter_by(user_id=user_id).all()
        allergies = MedicalGeneralInfoMedicationAllergy.query.filter_by(user_id=user_id).all()
        
        payload = {'gen_info': (genInfo if (current_user.user_id == user_id or 'general_medical_info' in g.get('clinical_care_authorized_resources')) else None),
                   'medications': (medications if (current_user.user_id == user_id or 'medications' in g.get('clinical_care_authorized_resources')) else None),
                   'allergies': (allergies if (current_user.user_id == user_id or 'medications' in g.get('clinical_care_authorized_resources')) else None)}
        return payload

    @token_auth.login_required(staff_role=('medical_doctor',), resources=('medications', 'general_medical_info'))
    @accepts(schema=MedicalGeneralInfoInputSchema(exclude=['medications.idx','allergies.idx']), api=ns)
    @responds(schema=MedicalGeneralInfoInputSchema(exclude=['medications.idx','allergies.idx']), status_code=201, api=ns)
    def post(self, user_id):
        '''
        Post request to post the client's onboarding personal and family history
        '''
        current_user, _ = token_auth.current_user()
        user_is_self = (True if current_user.user_id == user_id else False)

        # First check if the client exists
        self.check_user(user_id, user_type='client')
        payload = {}

        # If the user submits something for general history, then removes it from the payload, 
        # remove the everything for that user in general history table

        gen_info_current = MedicalGeneralInfo.query.filter_by(user_id=user_id).one_or_none()
        if gen_info_current and (user_is_self or 'general_medical_info' in g.get('clinical_care_authorized_resources')):
            if gen_info_current:
                db.session.delete(gen_info_current)

        generalInfo = request.parsed_obj['gen_info']
        if generalInfo and (user_is_self or 'general_medical_info' in g.get('clinical_care_authorized_resources')):
            if generalInfo.primary_doctor_contact_name:
                # If the client has a primary care doctor, we need either the 
                # phone number or email
                if not generalInfo.primary_doctor_contact_phone and \
                    not generalInfo.primary_doctor_contact_email:
                    db.session.rollback()
                    raise BadRequest('If a primary doctor name is given, the client must also '
                                     'provide the doctors phone number or email')

            if generalInfo.blood_type or generalInfo.blood_type_positive is not None:
                # if the client starts by indication which blood type they have or the sign
                # they also need the other.
                if generalInfo.blood_type is None or generalInfo.blood_type_positive is None:
                    db.session.rollback()
                    raise BadRequest('If bloodtype or sign is given, client must provide both.')

            generalInfo.user_id = user_id
            db.session.add(generalInfo)

            payload['gen_info'] = generalInfo

        # Before storing data, delete what exists in the database
        # If the user submits something for medication history, then removes it from the payload, 
        # remove everything for that user in medication history table
        meds = MedicalGeneralInfoMedications.query.filter_by(user_id=user_id).all()
        if meds and (user_is_self or 'medications' in g.get('clinical_care_authorized_resources')):
            if meds:
                for med in meds:
                    db.session.delete(med)

        medications = request.parsed_obj['medications']
        if medications and (user_is_self or 'medications' in g.get('clinical_care_authorized_resources')):
            payload['medications'] = []
            for medication in medications:
                # If the client is taking medications, they MUST tell us what
                # medication
                if medication.medication_name is None:
                    db.session.rollback()
                    raise BadRequest('Medication name required.')
                else:
                    # If the client gives a medication dosage, they must also give 
                    # the units
                    if medication.medication_dosage and medication.medication_units is None:
                        db.session.rollback()
                        raise BadRequest('Medication dosage units required.')

                    if medication.medication_freq:
                        if medication.medication_times_per_freq is None and medication.medication_time_units is None:
                            db.session.rollback()
                            raise BadRequest('Medication frequency and time unit required.')

                    medication.user_id = user_id
                    medication.reporter_id = token_auth.current_user()[0].user_id
                    db.session.add(medication)

                    payload['medications'].append(medication)
            
        # If the user submits something for allergy history, then removes it from the payload, 
        # remove everything for that user in allergy history table

        # If the client is allergic to certain medication, they MUST tell us what
        # medication
        allergies_current = MedicalGeneralInfoMedicationAllergy.query.filter_by(user_id=user_id).all()
        if allergies_current and (user_is_self or 'medications' in g.get('clinical_care_authorized_resources')):
            for allergy in allergies_current:
                db.session.delete(allergy)

        allergies = request.parsed_obj['allergies']
        if allergies and (user_is_self or 'medications' in g.get('clinical_care_authorized_resources')):
            payload['allergies'] = []

            for allergicTo in allergies:
                if not allergicTo.medication_name:
                    # If the client indicates they have an allergy to a medication
                    # they must AT LEAST send the name of the medication they are allergic to
                    db.session.rollback()
                    raise BadRequest('Name of medication with allergic reaction required.')
                else:
                    allergicTo.user_id = user_id
                    payload['allergies'].append(allergicTo)
                    db.session.add(allergicTo)      

        # insert results into the result table
        db.session.commit()
        return payload


@ns.route('/medicalinfo/general/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedicalGeneralInformation(BaseResource):
    @token_auth.login_required(resources=('general_medical_info',))
    @responds(schema=MedicalGeneralInfoSchema, api=ns)
    def get(self, user_id):
        '''
        This request gets the users personal and family history if it exists
        '''
        self.check_user(user_id, user_type='client')
        genInfo = MedicalGeneralInfo.query.filter_by(user_id=user_id).first()
        payload = {'general_info': genInfo}
        return genInfo

    @token_auth.login_required(staff_role=('medical_doctor',), resources=('general_medical_info',))
    @accepts(schema=MedicalGeneralInfoSchema, api=ns)
    @responds(schema=MedicalGeneralInfoSchema, status_code=201, api=ns)
    def post(self, user_id):
        '''
        Post request to post the client's onboarding personal and family history
        '''
        # First check if the client exists
        self.check_user(user_id, user_type='client')

        generalInfo = request.parsed_obj
        if generalInfo:
            if generalInfo.primary_doctor_contact_name:
                # If the client has a primary care doctor, we need either the 
                # phone number or email
                if not generalInfo.primary_doctor_contact_phone and \
                    not generalInfo.primary_doctor_contact_email:
                    raise BadRequest('If a primary doctor name is given, the client must also '
                                     'provide the doctors phone number or email')

            if generalInfo.blood_type or generalInfo.blood_type_positive:
                # if the client starts by indication which blood type they have or the sign
                # they also need the other.
                if generalInfo.blood_type is None or generalInfo.blood_type_positive is None:
                    raise BadRequest('If bloodtype or sign is given, client must provide both.')
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

    @token_auth.login_required(staff_role=('medical_doctor',), resources=('general_medical_info',))
    @accepts(schema=MedicalGeneralInfoSchema, api=ns)
    @responds(schema=MedicalGeneralInfoSchema, status_code=201, api=ns)
    def put(self, user_id):
        '''
        Put request to update the client's onboarding personal and family history
        '''
        self.check_user(user_id, user_type='client')

        generalInfo = request.json
        if generalInfo:
            # del generalInfo.__dict__['_sa_instance_state']
            if generalInfo.get('primary_doctor_contact_name'):
                # If the client has a primary care doctor, we need either the 
                # phone number or email
                if not generalInfo.get('primary_doctor_contact_phone') and \
                    not generalInfo.get('primary_doctor_contact_email'):
                    raise BadRequest('If a primary doctor name is given, the client must also '
                                     'provide the doctors phone number or email')

            if generalInfo.get('blood_type') or generalInfo.get('blood_type_positive'):
                # if the client starts by indication which blood type they have or the sign
                # they also need the other.
                if generalInfo.get('blood_type') is None or generalInfo.get('blood_type_positive') is None:
                    raise BadRequest('If bloodtype or sign is given, client must provide both.')
                else:
                    generalInfo['user_id'] = user_id
            genInfo = MedicalGeneralInfo.query.filter_by(user_id=user_id).one_or_none()
            genInfo.update(generalInfo)
        
        # insert results into the result table
        db.session.commit()
        return generalInfo

@ns.route('/medicalinfo/medications/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedicalMedicationInformation(BaseResource):
    # Multiple medications per user allowed
    __check_resource__ = False

    @token_auth.login_required(resources=('medications',))
    @responds(schema=MedicalMedicationsInfoInputSchema, api=ns)
    def get(self, user_id):
        '''
        This request gets the users personal and family history if it exists
        '''
        self.check_user(user_id, user_type='client')

        medications = MedicalGeneralInfoMedications.query.filter_by(user_id=user_id).all()
        payload = {'medications': medications}
        return payload

    @token_auth.login_required(staff_role=('medical_doctor',), resources=('medications',))
    @accepts(schema=MedicalMedicationsInfoInputSchema(exclude=['medications.idx']), api=ns)
    @responds(schema=MedicalMedicationsInfoInputSchema, status_code=201, api=ns)
    def post(self, user_id):
        '''
        Post request to post the client's onboarding personal and family history
        '''
        self.check_user(user_id, user_type='client')
        
        payload = {}

        if request.parsed_obj['medications']:
            medications = request.parsed_obj['medications']
            payload['medications'] = []

            for medication in medications:
                # If the client is taking medications, they MUST tell us what
                # medication
                if not medication.medication_name:
                    raise BadRequest('Medication name required.')
                else:
                    # If the client gives a medication dosage, they must also give 
                    # the units
                    if medication.medication_dosage and not medication.medication_units:
                        raise BadRequest('Medication dosage units required.')

                    if medication.medication_freq:
                        if not medication.medication_times_per_freq and not medication.medication_time_units:
                            raise BadRequest('Medication frequency and time unit required.')
                    medication.user_id = user_id
                    medication.reporter_id = token_auth.current_user()[0].user_id
                    payload['medications'].append(medication)
                    db.session.add(medication)    
        
        # insert results into the result table
        db.session.commit()
        return payload

    @token_auth.login_required(staff_role=('medical_doctor',), resources=('medications',))
    @accepts(schema=MedicalMedicationsInfoInputSchema, api=ns)
    @responds(schema=MedicalMedicationsInfoInputSchema, status_code=201, api=ns)
    def put(self, user_id):
        '''
        Put request to update the client's onboarding personal and family history
        '''
        self.check_user(user_id, user_type='client')

        payload = {}

        if request.parsed_obj['medications']:
            medications = request.parsed_obj['medications']
            payload['medications'] = []
            for medication in medications:
                # If the client is taking medications, they MUST tell us what
                # medication
                if not medication.medication_name:
                    raise BadRequest('Medication name required.')
                else:
                    # If the client gives a medication dosage, they must also give 
                    # the units
                    if medication.medication_dosage and not medication.medication_units:
                        raise BadRequest('Medication dosage units required.')

                    if medication.medication_freq:
                        if not medication.medication_times_per_freq and not medication.medication_time_units:
                            raise BadRequest('Medication frequency and time unit required.')

                    medication.__dict__['user_id'] = user_id
                    # If medication and user are in it already, then send an update
                    # else, add it to the db
                    medicationInDB = MedicalGeneralInfoMedications.query.filter_by(user_id=user_id).filter_by(idx=medication.idx).one_or_none()
                    if medicationInDB:
                        del medication.__dict__['_sa_instance_state']
                        medicationInDB.update(medication.__dict__)
                    else: 
                        raise BadRequest('Medication table not found, use POST first.')
                    
                    payload['medications'].append(medication)
        
        # insert results into the result table
        db.session.commit()
        return payload        

    @token_auth.login_required(staff_role=('medical_doctor',), resources=('medications',))
    @accepts(schema=CheckBoxArrayDeleteSchema, api=ns)
    @responds(status_code=201, api=ns)
    def delete(self, user_id):
        '''
        Put request to update the client's onboarding personal and family history
        '''
        payload = {}

        self.check_user(user_id, user_type='client')
        
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
class MedicalAllergiesInformation(BaseResource):
    # Multiple allergies per user allowed
    __check_resource__ = False

    @token_auth.login_required(resources=('medications',))
    @responds(schema=MedicalAllergiesInfoInputSchema, api=ns)
    def get(self, user_id):
        '''
        This request gets the users personal and family history if it exists
        '''
        self.check_user(user_id, user_type='client')

        allergies = MedicalGeneralInfoMedicationAllergy.query.filter_by(user_id=user_id).all()
        payload = {'allergies': allergies}
        return payload

    @token_auth.login_required(staff_role=('medical_doctor',), resources=('medications',))
    @accepts(schema=MedicalAllergiesInfoInputSchema(exclude=['allergies.idx']), api=ns)
    @responds(schema=MedicalAllergiesInfoInputSchema, status_code=201, api=ns)
    def post(self, user_id):
        '''
        Post request to post the client's onboarding personal and family history
        '''
        # First check if the client exists
        self.check_user(user_id, user_type='client')
        
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
                    raise BadRequest('Name of medication with allergic reaction required.')
                else:
                    allergicTo.user_id = user_id
                    payload['allergies'].append(allergicTo)
                    db.session.add(allergicTo)      
        
        # insert results into the result table
        db.session.commit()
        return payload

    @token_auth.login_required(staff_role=('medical_doctor',), resources=('medications',))
    @accepts(schema=MedicalAllergiesInfoInputSchema, api=ns)
    @responds(schema=MedicalAllergiesInfoInputSchema, status_code=201, api=ns)
    def put(self, user_id):
        '''
        Put request to update the client's onboarding personal and family history
        '''
        payload = {}

        self.check_user(user_id, user_type='client')

        # If the client is allergic to certain medication, they MUST tell us what
        # medication
        if request.parsed_obj['allergies']:
            allergies = request.parsed_obj['allergies']
            payload['allergies'] = []
            for allergicTo in allergies:
                if not allergicTo.medication_name:
                    # If the client indicates they have an allergy to a medication
                    # they must AT LEAST send the name of the medication they are allergic to
                    raise BadRequest('Name of medication with allergic reaction required.')
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

    @token_auth.login_required(staff_role=('medical_doctor',), resources=('medications',))
    @accepts(schema=CheckBoxArrayDeleteSchema, api=ns)
    @responds(status_code=201, api=ns)
    def delete(self, user_id):
        '''
        delete request to update the client's onboarding personal and family history
        '''

        self.check_user(user_id, user_type='client')
        
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
class MedicalLookUpSTDResource(BaseResource):
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

@ns.route('/medicalinfo/social/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedicalSocialHist(BaseResource):
    @token_auth.login_required(resources=('sexual_history','social_history'))
    @responds(schema=MedicalSocialHistoryOutputSchema, api=ns)
    def get(self, user_id):
        """ This request retrieves the social history
        for client ``user_id`` in response to a GET request.

        The example returned payload will look like::

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
        current_user, _ = token_auth.current_user()
        self.check_user(user_id, user_type='client')

        social_hist = MedicalSocialHistory.query.filter_by(user_id=user_id).one_or_none()
        std_hist = MedicalSTDHistory.query.filter_by(user_id=user_id).all()

        payload = {'social_history': (social_hist if (current_user.user_id == user_id or 'social_history' in g.get('clinical_care_authorized_resources')) else None),
                   'std_history': (std_hist if (current_user.user_id == user_id or 'sexual_history' in g.get('clinical_care_authorized_resources')) else None)}
        return payload

    @token_auth.login_required(staff_role=('medical_doctor',), resources=('sexual_history','social_history'))
    @accepts(schema=MedicalSocialHistoryOutputSchema, api=ns)
    @responds(schema=MedicalSocialHistoryOutputSchema, status_code=201, api=ns)
    def post(self, user_id):
        """ This request submits the social history
        for client ``user_id`` in response to a POST request.

        The example returned payload will look like::

            {
                "social_history":{
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
                    {"std_id": int}
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
        current_user, _ = token_auth.current_user()
        self.check_user(user_id, user_type='client')
        # Check if this information is already in the DB

        # Check if this information is already in the DB
        payload = {}

        social = request.parsed_obj['social_history']

        # If the user submits something for Social history, then removes it from the payload, 
        # remove the everything for that user in social history table
        if social and (current_user.user_id == user_id or 'social_history' in g.get('clinical_care_authorized_resources')):
            social_hist_current = MedicalSocialHistory.query.filter_by(user_id=user_id).one_or_none()
            if social_hist_current:
                db.session.delete(social_hist_current)

            if social.last_smoke_time == '':
                social.last_smoke_time = None
            
            if social.ever_smoked:
                if not social.currently_smoke:
                    # if last smoke or last smoke time (months/years)
                    # is present, then both must be present
                    if social.last_smoke or social.last_smoke_time:
                        if social.last_smoke is None or social.last_smoke_time is None: 
                            db.session.rollback()
                            raise BadRequest('Date of last smoked and duration required.')
                        
                        if(social.last_smoke_time == 'days'):
                            social.__dict__['last_smoke_date'] = datetime.now() - relativedelta(months=social.last_smoke) 
                        elif(social.last_smoke_time == 'months'):
                            social.__dict__['last_smoke_date'] = datetime.now() - relativedelta(months=social.last_smoke)
                        elif(social.last_smoke_time == 'years'):
                            social.__dict__['last_smoke_date'] = datetime.now() - relativedelta(years=social.last_smoke)
            social.__dict__['user_id'] = user_id

            db.session.add(social)

            payload['social_history'] = social

        # If the user submits something for STD history, then removes it from the payload, 
        # remove their STD history from the table
        stds = request.parsed_obj['std_history']
        if stds and (current_user.user_id == user_id or 'sexual_history' in g.get('clinical_care_authorized_resources')):
            std_history_current = MedicalSTDHistory.query.filter_by(user_id=user_id).all()
            # If the payload contains an STD for a user already, then just continue
            if std_history_current:
                for std in std_history_current:
                    db.session.delete(std)
            
            payload['std_history'] = []

            for std in stds:
                stdInDB = MedicalLookUpSTD.query.filter_by(std_id=std.std_id).one_or_none()
                if not stdInDB:
                    db.session.rollback()
                    raise BadRequest('STD ID not found.')

                std.user_id = user_id
                db.session.add(std)
                payload['std_history'].append(std)

        # insert results into the result table
        db.session.commit()
        return payload

@ns.route('/medicalconditions/')
class MedicalCondition(BaseResource):
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
class MedicalFamilyHist(BaseResource):
    @token_auth.login_required(resources=('personal_medical_history',))
    @responds(schema=MedicalFamilyHistOutputSchema, api=ns)
    def get(self, user_id):
        '''
        This request gets the users personal and family history if it exists
        '''
        self.check_user(user_id, user_type='client')

        client_personalfamilyhist = MedicalFamilyHistory.query.filter_by(user_id=user_id).all()
        payload = {'items': client_personalfamilyhist,
                   'total_items': len(client_personalfamilyhist)}
        return payload

    @token_auth.login_required(staff_role=('medical_doctor',), resources=('personal_medical_history',))
    @accepts(schema=MedicalFamilyHistInputSchema, api=ns)
    @responds(schema=MedicalFamilyHistOutputSchema, status_code=201, api=ns)
    def post(self, user_id):
        '''
        Post request to post the client's onboarding personal and family history
        '''
        self.check_user(user_id, user_type='client')
        
        # the data expected for the backend is:
        # parameter: user_id 
        # payload: medical_condition_id, myself, father, mother, brother, sister

        for result in request.parsed_obj['conditions']:
            check_medical_condition_existence(result.medical_condition_id)
            user_and_medcon = MedicalFamilyHistory.query.filter_by(user_id=user_id).filter_by(medical_condition_id=result.medical_condition_id).one_or_none()
            if user_and_medcon:
                raise BadRequest(f'Medical condition {result.medical_condition_id} '
                                 f'already exists for user {user_id}.')

            result.user_id = user_id
            db.session.add(result)
        payload = {'items': request.parsed_obj['conditions'],
                   'total_items': len(request.parsed_obj['conditions'])}
        # insert results into the result table
        db.session.commit()
        return payload

    @token_auth.login_required(staff_role=('medical_doctor',), resources=('personal_medical_history',))
    @accepts(schema=MedicalFamilyHistInputSchema, api=ns)
    @responds(schema=MedicalFamilyHistOutputSchema, status_code=201, api=ns)
    def put(self, user_id):
        '''
        Put request to update the client's onboarding personal and family history
        '''
        self.check_user(user_id, user_type='client')
        
        # the data expected for the backend is:
        # parameter: user_id 
        # payload: medical_condition_id, myself, father, mother, brother, sister
        for idx,result in enumerate(request.parsed_obj['conditions']):
            check_medical_condition_existence(result.medical_condition_id)
            user_and_medcon = MedicalFamilyHistory.query.filter_by(user_id=user_id).filter_by(medical_condition_id=result.medical_condition_id).one_or_none()
            if user_and_medcon:
                user_and_medcon.update(request.json['conditions'][idx])
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
class MedImaging(BaseResource):
    __check_resource__ = False
    
    @token_auth.login_required(resources=('diagnostic_imaging',))
    @responds(schema=MedicalImagingSchema(many=True), api=ns)
    def get(self, user_id):
        """returns a json file of all the medical images in the database for the specified user_id

            Note:
            image_path is a sharable url for an image saved in S3 Bucket,
            if running locally, it is the path to a local temp file
        """
        self.check_user(user_id, user_type='client')

        query = db.session.query(
                    MedicalImaging, User.firstname, User.lastname
                ).filter(
                    MedicalImaging.user_id == user_id
                ).filter(
                    MedicalImaging.reporter_id == User.user_id
                ).all()
        
        # prepare response with reporter info
        response = []
        for data in query:
            img_dat = data[0].__dict__
            img_dat.update({'reporter_firstname': data[1], 'reporter_lastname': data[2]})
            response.append(img_dat)

        #get presigned link for AWS for each image being returned
        fh = FileHandling()
        for img in response:
            if img.get('image_path'):
                img['image_path'] = fh.get_presigned_url(img.get('image_path'))

        return response

    #Unable to use @accepts because the input files come in a form-data, not json.
    @token_auth.login_required(staff_role=('medical_doctor',), resources=('diagnostic_imaging',))
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
        self.check_user(user_id, user_type='client')

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
        data_list = []
        hex_token = secrets.token_hex(4)

        # add all files to S3
        # format: id{user_id:05d}/medical_images/img_type_date_hex_token_i.img_extension
        fh = FileHandling()
        img = request.files['image']
        _prefix = f'id{user_id:05d}/medical_images'

        for i, img in enumerate(files.getlist('image')):
            # validate file size - safe threashold (MAX = 10 mb)
            fh.validate_file_size(img, IMAGE_MAX_SIZE)
            # validate file type
            img_extension = fh.validate_file_type(img, MED_ALLOWED_IMAGE_TYPES)

            mi_data = mi_schema.load(request.form)
            mi_data.user_id = user_id
            mi_data.reporter_id = reporter.user_id
            date = mi_data.image_date

            # Save image to S3
            s3key = f'{_prefix}/{mi_data.image_type}_{date}_{hex_token}_{i}{img_extension}'
            fh.save_file_to_s3(img, s3key)
            mi_data.image_path = s3key

            data_list.append(mi_data)

        db.session.add_all(data_list)  
        db.session.commit()

    @ns.doc(params={'image_id': 'ID of the image to be deleted'})
    @token_auth.login_required(staff_role=('medical_doctor',), resources=('diagnostic_imaging',))
    @responds(status_code=204, api=ns)
    def delete(self, user_id):
        idx = request.args.get('image_id', type=int)

        if idx:
            data = MedicalImaging.query.filter_by(user_id=user_id, idx=idx).one_or_none()
            if not data:
                raise BadRequest(f'Image {idx} not found.')

            #ensure logged in user is the reporter for this image
            self.check_ehr_permissions(data)

            #delete image saved in S3 bucket
            fh = FileHandling()
            fh.delete_from_s3(prefix=data.image_path)

            db.session.delete(data)
            db.session.commit()
        else:
            raise BadRequest("image_id must be an integer.")   


@ns.route('/bloodtest/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedBloodTest(BaseResource):
    
    # Multiple tests per user allowed
    __check_resource__ = False
    
    @token_auth.login_required(staff_role=('medical_doctor',), resources=('blood_chemistry',))
    @accepts(schema=MedicalBloodTestsInputSchema, api=ns)
    @responds(schema=MedicalBloodTestSchema, status_code=201, api=ns)
    def post(self, user_id):
        """
        Resource to submit a new blood test instance for the specified client.

        Test submissions are given a test_id which can be used to reference back
        to the results related to this submisison. Each submission may have 
        multiple results (e.g. in a panel)
        """
        
        self.check_user(user_id, user_type='client')
        
        # remove results from data, commit test info without results to db
        results = request.parsed_obj['results']
        
        #insert non results data into MedicalBloodTests in order to generate the test_id
        client_bt = MedicalBloodTests(**{
            'user_id': user_id,
            'reporter_id': token_auth.current_user()[0].user_id,
            'date': request.parsed_obj['date'],
            'notes': request.parsed_obj['notes']
        })
        
        db.session.add(client_bt)
        db.session.commit()
        
        #for each provided result, evaluate the results based on the range that most applies to the client
        for result in results:
            ranges = LookupBloodTestRanges.query.filter_by(modobio_test_code=result['modobio_test_code']).all()
            client = User.query.filter_by(user_id=user_id).one_or_none()
                
            if len(ranges) > 1:
                
                #calculate client age
                today = date.today()
                client_age = today.year - client.dob.year
                if today.month < client.dob.month or (today.month == client.dob.month and today.day < client.dob.day):
                    client_age -= 1
                
                for range in ranges:
                    #prune ranges by age if relevant
                    age_min = range.age_min
                    if age_min == None:
                        age_min = 0
                    age_max = range.age_max
                    if age_max == None:
                        age_max = 999
                    if not (age_min <= client_age <= age_max):
                        #if client's age does not apply to this range's age range, remove it from the remaining ranges
                        ranges.remove(range)
                result['age'] = client_age
                
                #first prune by client biological sex if relevant
                for range in ranges:
                    if range.biological_sex_male != None:
                        if range.biological_sex_male == client.biological_sex_male:
                            if not client.biological_sex_male:
                                #prune by menstrual cycle if relevant
                                client_cycle = ClientFertility.query.filter_by(user_id=user_id).order_by(ClientFertility.created_at.desc()).first()
                                if client_cycle == 'unknown' and range.menstrual_cycle != None:
                                    ranges.remove(range)
                                elif client_cycle != range.menstrual_cycle:
                                    ranges.remove(range)
                                else:
                                    result['menstrual_cycle'] = client_cycle


                client_races = []
                for race in ClientRaceAndEthnicity.query.filter_by(user_id=user_id).all():
                    client_races.append(race.race_id)
        
                #prune remaining ranges by races relevant to the client
                for range in ranges:
                    if range.race_id != None and range.race_id not in client_races:
                        ranges.remove(range)
                
                if len(ranges) > 1:
                    """
                    If more than 1 range remains at this point, it is because the client has multiple
                    races that can impact the evaluation. In this case, we want the 'most conservative'
                    range. Meaning of all the remaining ranges, we want to take the highest min values
                    and lowest max values.
                    """
                    critical_min = ref_min = 0
                    critical_max = ref_max = float("inf")
                    races = []
                    for range in ranges:
                        if range.critical_min != None and range.critical_min > critical_min:
                            critical_min = range.critical_min
                        if range.ref_min != None and range.ref_min > ref_min:
                            ref_min = range.ref_min
                        if range.ref_max != None and range.ref_max < ref_max:
                            ref_max = range.ref_max
                        if range.critical_max != None and range.critical_max < critical_max:
                            critical_max = range.critical_max
                        if range.race_id != None:
                            races.append(LookupRaces.query.filter_by(race_id=range.race_id).one_or_none().race_name)
                    if len(races) > 0:
                        result['race'] = ','.join(races)
                    eval_values = {
                        'critical_min': critical_min,
                        'ref_min': ref_min,
                        'ref_max': ref_max,
                        'critical_max': critical_max
                    }
            else:
                eval_values = {
                    'critical_min': ranges[0].critical_min,
                    'ref_min': ranges[0].ref_min,
                    'ref_max': ranges[0].ref_max,
                    'critical_max': ranges[0].critical_max
                }

            #make the evaluation based on the eval values found above
            if result['result_value'] < eval_values['critical_min']:
                result['evaluation'] = 'critical'
            elif result['result_value'] < eval_values['ref_min']:
                result['evaluation'] = 'abnormal'
            elif result['result_value'] < eval_values['ref_max']:
                result['evaluation'] = 'normal'
            elif result['result_value'] < eval_values['critical_max']:
                result['evaluation'] = 'abnormal'
            else:
                result['evaluation'] = 'critical'
            result['test_id'] = client_bt.test_id
            db.session.add(MedicalBloodTestResults(**result))
            
        db.session.commit()
        
        return client_bt

    @token_auth.login_required(staff_role=('medical_doctor',), resources=('blood_chemistry',))
    @ns.doc(params={'test_id': 'int',})
    @responds(status_code=204, api=ns)
    def delete(self, user_id):
        '''
        Delete request for a client's blood test
        '''
        self.check_user(user_id, user_type='client')

        test_id = request.args.get('test_id', type=int)
        if test_id:
            result = MedicalBloodTests.query.filter_by(user_id=user_id, test_id=test_id).one_or_none()

            #ensure logged in user is the reporter for this test
            self.check_ehr_permissions(result)

            db.session.delete(result)
            db.session.commit()
        else:
            raise BadRequest("test_id must be an integer.")
        
@ns.route('/bloodtest/image/<int:test_id>/')
@ns.doc(params={'test_id': 'User ID number'})
class MedBloodTestImage(BaseResource):
    
    @token_auth.login_required(staff_role=('medical_doctor',), resources=('blood_chemistry',))
    @responds(schema=MedicalBloodTestSchema, api=ns, status_code=200)
    def patch(self, test_id):
        """
        This resource can be used to add an image to submitted blood test results.

        Args:
            image ([file]): image file to be added to test results (only .pdf files are supported, max size 20MB)
        """

        if not ('image' in request.files and request.files['image']):  
            raise BadRequest('No file selected.')

        # add all files to S3
        # format: id{user_id:05d}/bloodtest/id{test_id:05d}/hex_token.img_extension
        fh = FileHandling()
        img = request.files['image']
        
        # validate file size - safe threashold (MAX = 10 mb)
        fh.validate_file_size(img, BLOOD_TEST_IMAGE_MAX_SIZE)
        
        # validate file type
        img_extension = fh.validate_file_type(img, ('.pdf',))
        
        #get hex token
        hex_token = secrets.token_hex(4)
        
        test = MedicalBloodTests.query.filter_by(test_id=test_id).one_or_none()
        _prefix = f'id{test.user_id:05d}/bloodtest/id{test.test_id:05d}'

        # if any, delete files with prefix
        fh.delete_from_s3(prefix=_prefix)

        # Save to S3
        s3key = f'{_prefix}/{hex_token}{img_extension}'
        fh.save_file_to_s3(img, s3key)

        #store file path in db
        test.image_path = s3key
        db.session.commit()
        
        return test

@ns.route('/bloodtest/all/<int:user_id>/')
@ns.doc(params={'user_id': 'Client ID number'})
class MedBloodTestAll(BaseResource):
    @token_auth.login_required(resources=('blood_chemistry',))
    @responds(schema=AllMedicalBloodTestSchema, api=ns)
    def get(self, user_id):
        """
        This resource returns every instance of blood test submissions for the specified user_id

        Each test submission includes the following data:
        - date
        - test_id
        - notes
        - reporter (a staff member who reported the test results)
        
        To see the actual test results for a given test, use the test_id
        to query the (GET) `/bloodtest/results/<int:test_id>/` endpoint

        To see test results for every blood test submission for a specified client, 
        use the (GET)`/bloodtest/results/all/<int:user_id>/` endpoint. 
        """
        self.check_user(user_id, user_type='client')

        blood_tests =  db.session.query(
                    MedicalBloodTests, User.firstname, User.lastname
                ).filter(
                    MedicalBloodTests.reporter_id == User.user_id
                ).filter(
                    MedicalBloodTests.user_id == user_id
                ).all()

        # prepare response items with reporter name from User table
        response = []
        fh = FileHandling()
        for test in blood_tests:
            data = test[0].__dict__
            data.update(
                {'reporter_firstname': test[1],
                 'reporter_lastname': test[2],
                 'image': fh.get_presigned_url(test[0].image_path)})
            response.append(data)
        payload = {}
        payload['items'] = response
        payload['total'] = len(blood_tests)
        payload['user_id'] = user_id
        return payload


@ns.route('/bloodtest/results/<int:test_id>/')
@ns.doc(params={'test_id': 'Test ID number'})
class MedBloodTestResults(BaseResource):
    """
    Resource for working with a single blood test 
    entry instance, test_id.

    Each test instance may have multiple test results. 
    """
    @token_auth.login_required(resources=('blood_chemistry',))
    @responds(schema=MedicalBloodTestResultsOutputSchema, api=ns)
    def get(self, test_id):
        """
        Returns details of the test denoted by test_id as well as 
        the actual results submitted.
        """
        #query for join of MedicalBloodTestResults and MedicalBloodTestResultTypes table

        results =  db.session.query(
                MedicalBloodTests, MedicalBloodTestResults, LookupBloodTests, User
                ).join(
                    LookupBloodTests
                ).join(MedicalBloodTests
                ).filter(
                    MedicalBloodTests.test_id == MedicalBloodTestResults.test_id
                ).filter(
                    MedicalBloodTests.test_id==test_id
                ).filter(
                    MedicalBloodTests.reporter_id == User.user_id
                ).all()

        if not results:
            return
        fh = FileHandling()
        if results[0][0].image_path:
            image_path = fh.get_presigned_url(results[0][0].image_path)
        else:
            image_path = None
        # prepare response with test details   
        nested_results = {'test_id': test_id, 
                          'date' : results[0][0].date,
                          'notes' : results[0][0].notes,
                          'image': image_path,
                          'reporter_id': results[0][0].reporter_id,
                          'reporter_firstname': results[0][3].firstname,
                          'reporter_lastname': results[0][3].lastname,
                          'results': []} 
        
        # loop through results in order to nest results in their respective test
        # entry instances (test_id)
        for _, test_result, result_type, _ in results:
                res = {
                    'modobio_test_code': result_type.modobio_test_code, 
                    'result_value': test_result.result_value,
                    'evaluation': test_result.evaluation,
                    'age': test_result.age,
                    'biological_sex_male': test_result.biological_sex_male,
                    'race': test_result.race,
                    'menstrual_cycle': test_result.menstrual_cycle
                }
                nested_results['results'].append(res)

        payload = {}
        payload['items'] = [nested_results]
        payload['tests'] = 1
        payload['test_results'] = len( nested_results['results'])
        payload['user_id'] = results[0][0].user_id
        return payload

@ns.route('/bloodtest/results/all/<int:user_id>/')
@ns.doc(params={'user_id': 'Client ID number'})
class AllMedBloodTestResults(BaseResource):
    """
    Endpoint for returning all blood test results from a client.

    This includes all test submisison details along with the test
    results associated with each test submission. 
    """
    @token_auth.login_required(resources=('blood_chemistry',))
    @responds(schema=MedicalBloodTestResultsOutputSchema, api=ns)
    def get(self, user_id):
        self.check_user(user_id, user_type='client')

        # pull up all tests, test results, and the test type names for this client
        results =  db.session.query(
                        MedicalBloodTests, MedicalBloodTestResults, LookupBloodTests, User
                        ).join(
                            LookupBloodTests
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
                    res = {
                        'modobio_test_code': result_type.modobio_test_code, 
                        'result_value': test_result.result_value,
                        'evaluation': test_result.evaluation,
                        'age': test_result.age,
                        'biological_sex_male': test_result.biological_sex_male,
                        'race': test_result.race,
                        'menstrual_cycle': test_result.menstrual_cycle
                    }
                    test['results'].append(res)
                    # add test details if not present
                    if not test.get('date', False):
                        test['date'] = test_info.date
                        test['notes'] = test_info.notes
        payload = {}
        payload['items'] = nested_results
        payload['tests'] = len(test_ids)
        payload['test_results'] = len(results)
        payload['user_id'] = user_id
        return payload

@ns.deprecated
@ns.route('/bloodtest/result-types/')
class MedBloodTestResultTypes(BaseResource):
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
@ns.deprecated
class MedHistory(BaseResource):
    @token_auth.login_required()
    @responds(schema=MedicalHistorySchema, api=ns)
    def get(self, user_id):
        """returns client's medical history as a json for the user_id specified"""
        self.check_user(user_id, user_type='client')

        client = MedicalHistory.query.filter_by(user_id=user_id).first()
        return client

    @token_auth.login_required(staff_role=('medical_doctor',))
    @accepts(schema=MedicalHistorySchema, api=ns)
    @responds(schema=MedicalHistorySchema, status_code=201, api=ns)
    def post(self, user_id):
        """returns client's medical history as a json for the user_id specified"""
        self.check_user(user_id, user_type='client')

        current_med_history = MedicalHistory.query.filter_by(user_id=user_id).first()

        data = request.json
        data["user_id"] = user_id

        mh_schema = MedicalHistorySchema()

        client_mh = mh_schema.load(data)

        db.session.add(client_mh)

        db.session.commit()

        return client_mh

    @token_auth.login_required(staff_role=('medical_doctor',))
    @accepts(schema=MedicalHistorySchema, api=ns)
    @responds(schema=MedicalHistorySchema, api=ns)
    def put(self, user_id):
        """updates client's medical history as a json for the user_id specified"""
        self.check_user(user_id, user_type='client')

        client_mh = MedicalHistory.query.filter_by(user_id=user_id).first()

        # get payload and update the current instance followd by db commit
        data = request.json
        
        data['last_examination_date'] = datetime.strptime(data['last_examination_date'], "%Y-%m-%d")
            
        # update resource 
        client_mh.update(data)

        db.session.commit()

        return client_mh


@ns.route('/physical/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedPhysical(BaseResource):
    @token_auth.login_required()
    @responds(schema=MedicalPhysicalExamSchema(many=True), api=ns)
    def get(self, user_id):
        """returns all client's medical physical exams for the user_id specified"""
        self.check_user(user_id, user_type='client')

        query =  db.session.query(
                MedicalPhysicalExam, User.firstname, User.lastname
                ).filter(
                    MedicalPhysicalExam.user_id == user_id
                ).filter(
                    MedicalPhysicalExam.reporter_id == User.user_id
                ).all()

        # prepare response with staff name and medical physical data
        
        response = []
        for data in query:
            physical = data[0].__dict__    
            physical.update({'reporter_firstname': data[1], 'reporter_lastname': data[2]})
            response.append(physical)

        return response

    @token_auth.login_required(staff_role=('medical_doctor',))
    @accepts(schema=MedicalPhysicalExamSchema, api=ns)
    @responds(schema=MedicalPhysicalExamSchema, status_code=201, api=ns)
    def post(self, user_id):
        """creates new db entry of client's medical physical exam as a json for the clientuser_idid specified"""
        self.check_user(user_id, user_type='client')

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
class AllMedInstitutes(BaseResource):
    @token_auth.login_required
    @responds(schema=MedicalInstitutionsSchema(many=True), api=ns)
    def get(self):
        """returns all medical institutes currently in the database"""

        institutes = MedicalInstitutions.query.all()
        
        return institutes

@ns.route('/medicalinstitutions/recordid/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ExternalMedicalRecordIDs(BaseResource):
    @token_auth.login_required
    @accepts(schema=MedicalExternalMREntrySchema,  api=ns)
    @responds(schema=MedicalExternalMREntrySchema,status_code=201, api=ns)
    def post(self, user_id):
        """for submitting client medical record ids from external medical institutions"""
        self.check_user(user_id, user_type='client')

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
        self.check_user(user_id, user_type='client')

        client_med_record_ids = MedicalExternalMR.query.filter_by(user_id=user_id).all()

        return client_med_record_ids


@ns.route('/surgery/<int:user_id>/')
@ns.doc(params={'user_id': 'Client user ID number'})
class MedicalSurgeriesAPI(BaseResource):

    @token_auth.login_required(staff_role=('medical_doctor',))
    @accepts(schema=MedicalSurgeriesSchema,  api=ns)
    @responds(schema=MedicalSurgeriesSchema, status_code=201, api=ns)
    def post(self, user_id):
        """register a client surgery in the db"""
        #check client and reporting staff have valid user ids
        self.check_user(user_id, user_type='client')
        self.set_reporter_id(request.parsed_obj)

        #add request data to db
        request.parsed_obj.user_id = user_id
        db.session.add(request.parsed_obj)
        db.session.commit()

        return request.parsed_obj

    @token_auth.login_required()
    @responds(schema=MedicalSurgeriesSchema(many=True), api=ns)
    def get(self, user_id):
        """returns a list of all surgeries for the given user_id"""
        self.check_user(user_id, user_type='client')

        return MedicalSurgeries.query.filter_by(user_id=user_id).all()

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
