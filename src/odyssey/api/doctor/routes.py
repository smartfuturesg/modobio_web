import logging
import secrets

from datetime import datetime, date

from dateutil.relativedelta import relativedelta
from flask import g, request, current_app, url_for
from flask_accepts import accepts, responds
from flask_restx import Namespace
from sqlalchemy import select, and_, or_
from werkzeug.exceptions import BadRequest

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
from odyssey.api.lookup.models import LookupBloodTests, LookupBloodTestRanges, LookupRaces
from odyssey.api.user.models import User, UserProfilePictures
from odyssey.utils.auth import token_auth
from odyssey.utils.misc import check_medical_condition_existence, date_validator
from odyssey.utils.files import FileDownload, FileUpload, ImageUpload, get_profile_pictures
from odyssey.utils.constants import ALLOWED_MEDICAL_IMAGE_TYPES, MEDICAL_IMAGE_MAX_SIZE
from odyssey.api.doctor.schemas import (
    AllMedicalBloodTestSchema,
    CheckBoxArrayDeleteSchema,
    MedicalBloodPressuresSchema,
    MedicalBloodPressuresOutputSchema,
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
    MedicalBloodTestResultsOutputSchema,
    MedicalBloodTestResultTypesSchema,
    MedicalImagingSchema,
    MedicalExternalMREntrySchema,
    MedicalExternalMRSchema,
    MedicalLookUpSTDOutputSchema,
    MedicalLookUpBloodPressureRangesOutputSchema,
    MedicalSocialHistoryOutputSchema,
    MedicalSurgeriesSchema,
    MedicalImagingOutputSchema,
)
from odyssey.api.client.models import ClientFertility, ClientRaceAndEthnicity
from odyssey.utils.base.resources import BaseResource

logger = logging.getLogger(__name__)

ns = Namespace('doctor', description='Operations related to doctor')
@ns.route('/bloodpressure/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedBloodPressures(BaseResource):
    # Multiple blood pressure measurements per user allowed
    __check_resource__ = False

    @token_auth.login_required(user_type=('client', 'provider'),resources=('blood_pressure',))
    @responds(schema=MedicalBloodPressuresOutputSchema, api=ns)
    def get(self, user_id):
        '''
        This request gets the users submitted blood pressure if it exists
        '''
        self.check_user(user_id, user_type='client')
        bp_info = MedicalBloodPressures.query.filter_by(user_id=user_id).all()
        
        reporter_pics = {} # key = user_id, value =  dict of pic links
        for data in bp_info:
            reporter = User.query.filter_by(user_id=data.reporter_id).one_or_none()
            data.reporter_firstname = reporter.firstname
            data.reporter_lastname = reporter.lastname

            if data.reporter_id != user_id and data.reporter_id not in reporter_pics:
                reporter_pics[data.reporter_id] = get_profile_pictures(data.reporter_id, True)            
            elif data.reporter_id not in reporter_pics:
                reporter_pics[data.reporter_id] = get_profile_pictures(user_id, False)
            
            data.reporter_profile_pictures = reporter_pics[data.reporter_id] 

        payload = {'items': bp_info,
                   'total_items': len(bp_info)}
        return payload

    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',), resources=('blood_pressure',))
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

    @token_auth.login_required(user_type=('client', 'provider'), user_type=('client', 'provider'), staff_role=('medical_doctor',), resources=('blood_pressure',))
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
    @token_auth.login_required(user_type=('client', 'provider'),resources=('medications', 'general_medical_info'))
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

    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',), resources=('medications', 'general_medical_info'))
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
    @token_auth.login_required(user_type=('client', 'provider'), resources=('general_medical_info',))
    @responds(schema=MedicalGeneralInfoSchema, api=ns)
    def get(self, user_id):
        '''
        This request gets the users personal and family history if it exists
        '''
        self.check_user(user_id, user_type='client')
        genInfo = MedicalGeneralInfo.query.filter_by(user_id=user_id).first()
        payload = {'general_info': genInfo}
        return genInfo

    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',), resources=('general_medical_info',))
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

    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',), resources=('general_medical_info',))
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

    @token_auth.login_required(user_type=('client', 'provider'), resources=('medications',))
    @responds(schema=MedicalMedicationsInfoInputSchema, api=ns)
    def get(self, user_id):
        '''
        This request gets the users personal and family history if it exists
        '''
        self.check_user(user_id, user_type='client')

        medications = MedicalGeneralInfoMedications.query.filter_by(user_id=user_id).all()
        payload = {'medications': medications}
        return payload

    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',), resources=('medications',))
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

    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',), resources=('medications',))
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

    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',), resources=('medications',))
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

    @token_auth.login_required(user_type=('client', 'provider'), resources=('medications',))
    @responds(schema=MedicalAllergiesInfoInputSchema, api=ns)
    def get(self, user_id):
        '''
        This request gets the users personal and family history if it exists
        '''
        self.check_user(user_id, user_type='client')

        allergies = MedicalGeneralInfoMedicationAllergy.query.filter_by(user_id=user_id).all()
        payload = {'allergies': allergies}
        return payload

    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',), resources=('medications',))
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

    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',), resources=('medications',))
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

    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',), resources=('medications',))
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
    @token_auth.login_required(user_type=('client', 'provider'),resources=('sexual_history', 'social_history'))
    @responds(schema=MedicalSocialHistoryOutputSchema, api=ns)
    def get(self, user_id):
        """ Social and sexual history information.

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
        care_team_resources = g.get('clinical_care_authorized_resources')

        payload = {}

        if (current_user.user_id == user_id or
            'social_history' in care_team_resources):
            social = MedicalSocialHistory.query.filter_by(user_id=user_id).one_or_none()
            payload['social_history'] = social

        if (current_user.user_id == user_id or
            'sexual_history' in care_team_resources):
            std = MedicalSTDHistory.query.filter_by(user_id=user_id).all()
            payload['std_history'] = std

        return payload

    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',), resources=('sexual_history', 'social_history'))
    @accepts(schema=MedicalSocialHistoryOutputSchema, api=ns)
    @responds(status_code=201, api=ns)
    def post(self, user_id):
        """ Update social and sexual history information.

        The two parts "social_history" and "sexual_history" can be updated independently
        from each other. For each part:

        1. If the part is not there, it will not be updated or deleted.
        2. If the part is there and contains data, it will override the current
           entry in the database.
        3. If the part is present but empty, the entry will be deleted from the database.

        Parameters
        ----------
        user_id : int
            User ID number.

        Returns
        -------
        dict
            JSON encoded dict.
        """
        # TODO: this is all kinds of wrong.
        # - POST method should be used to add new info for user only, not updates or deletes.
        # - There should be a PATCH method to allow partial updates of individual items.
        # - There should be a DELETE method to delete all info, not rely on empty body.
        # - This should be split into two endpoints, one for social and one for sexual.
        #   Why were they forced together?
        # - The use of multiple inputs for last_smoke_date (N as number + days/months/years
        #   as text) is infuriating. Backend should only deal with a datetime. Let
        #   frontend handle how it's entered.

        current_user, _ = token_auth.current_user()
        self.check_user(user_id, user_type='client')
        care_team_resources = g.get('clinical_care_authorized_resources')

        # If social_history is empty, it will get filled with 'missing' values from schema.
        social = request.parsed_obj['social_history']

        if (social and
            (current_user.user_id == user_id or
             'social_history' in care_team_resources)):

            if social.ever_smoked and not social.currently_smoke:
                # if last_smoke or last_smoke_time (in days/months/years) is present,
                # then both must be present
                if social.last_smoke is not None and social.last_smoke_time is None:
                    raise BadRequest('Last smoked date unit (days/months/years) is missing.')
                if social.last_smoke_time is not None and social.last_smoke is None:
                    raise BadRequest('Number of last smoked days/months/years is missing.')

                if(social.last_smoke_time == 'days'):
                    social.last_smoke_date = datetime.now() - relativedelta(days=social.last_smoke)
                elif(social.last_smoke_time == 'months'):
                    social.last_smoke_date = datetime.now() - relativedelta(months=social.last_smoke)
                elif(social.last_smoke_time == 'years'):
                    social.last_smoke_date = datetime.now() - relativedelta(years=social.last_smoke)
                else:
                    # both are None, clear entry
                    social.last_smoke_date = None

            social_current = MedicalSocialHistory.query.filter_by(user_id=user_id).one_or_none()

            if social_current:
                social_current.update(social)
            else:
                social.user_id = user_id
                db.session.add(social)

            db.session.commit()

        # stds is None if not present, empty list if deleting all entries, or list with entries.
        stds = request.parsed_obj['std_history']

        if (stds is not None and
            (current_user.user_id == user_id or
             'sexual_history' in care_team_resources)):

            stds_current = MedicalSTDHistory.query.filter_by(user_id=user_id).all()
            possible_stds = db.session.execute(select(MedicalLookUpSTD.std_id)).scalars().all()

            # Maps std_ids to instances, for both existing and requested
            existing = {s.std_id: s for s in stds_current}
            requested = {s.std_id: s for s in stds}

            to_add = set(requested.keys()) - set(existing.keys())
            to_del = set(existing.keys()) - set(requested.keys())

            invalid = to_add - set(possible_stds)
            if invalid:
                raise BadRequest(f'Invalid STD IDs: {invalid}')

            for std_id in to_del:
                db.session.delete(existing[std_id])
            for std_id in to_add:
                req = requested[std_id]
                req.user_id = user_id
                db.session.add(req)

        db.session.commit()


@ns.route('/medicalconditions/')
class MedicalCondition(BaseResource):
    """
    Returns the medical conditions currently documented in the DB
    """
    @token_auth.login_required(user_type=('client', 'provider'),)
    @responds(schema=MedicalConditionsOutputSchema,status_code=200, api=ns)
    def get(self):
        medcon_types = MedicalConditions.query.all()
        payload = {'items': medcon_types,
                   'total_items': len(medcon_types)}

        return payload

@ns.route('/familyhistory/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedicalFamilyHist(BaseResource):
    @token_auth.login_required(user_type=('client', 'provider'), resources=('personal_medical_history',))
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

    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',), resources=('personal_medical_history',))
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
            else:
                if result.myself or \
                    result.father or \
                    result.brother or \
                    result.mother or \
                    result.sister:
                    #only add if at least 1 value is true
                        result.user_id = user_id
                        db.session.add(result)
            
        db.session.commit()
        updated_history = MedicalFamilyHistory.query.filter_by(user_id=user_id).all()
        payload = {'items': updated_history,
                   'total_items': len(updated_history)}        
        return payload

    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',), resources=('personal_medical_history',))
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
                if request.json['conditions'][idx]['myself'] or \
                    request.json['conditions'][idx]['father'] or \
                    request.json['conditions'][idx]['brother'] or \
                    request.json['conditions'][idx]['mother'] or \
                    request.json['conditions'][idx]['sister']:
                        user_and_medcon.update(request.json['conditions'][idx])
                else:
                    #all conditions set to false, remove this row
                    db.session.delete(user_and_medcon)
            else:
                result.user_id = user_id
                db.session.add(result)
        
        db.session.commit()
        updated_history = MedicalFamilyHistory.query.filter_by(user_id=user_id).all()
        payload = {'items': updated_history,
                   'total_items': len(updated_history)}        
        return payload


@ns.route('/images/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedicalImagingEndpoint(BaseResource):
    __check_resource__ = False
    
    @token_auth.login_required(user_type=('client', 'provider'), resources=('diagnostic_imaging',))
    @responds(schema=MedicalImagingOutputSchema, status_code=200, api=ns)
    def get(self, user_id):
        """ Get all medical images for this user.

        Images are returned as URLs to the actual image on AWS S3.
        Along with the first name, last name, and profile picture as urls of the reporters of images
        Related by user id
        """
        self.check_user(user_id, user_type='client')

        med_images = (db.session.query(
                # Basically a right join, we still get all images for user but now also name and id of reporter
                MedicalImaging, User.firstname, User.lastname, User.user_id)
            .filter(
                MedicalImaging.user_id == user_id,
                MedicalImaging.reporter_id == User.user_id)
            .all())

        fd = FileDownload(user_id)

        images = []
        reporter_infos = {}
        for row in med_images:
            med_image, firstname, lastname, reporter_id = row
            images.append(med_image)

            # still need to check if already added reporter info to not call get_profile_pictures repeatedly
            if reporter_id not in reporter_infos.keys():
                their_pic = get_profile_pictures(reporter_id, True if reporter_id != user_id else False)
                reporter_infos[reporter_id] = {
                    'firstname': firstname,
                    'lastname': lastname,
                    'profile_pictures': their_pic,
                }

        # Serialize here, because we want to replace image_path with URL,
        # but only in the response, not store it in the DB.
        images = [item.__dict__ for item in images]
        for img in images:
            if img['image_path']:
                img['image_path'] = fd.url(img['image_path'])

        return {
            'reporter_infos': reporter_infos,
            'images': images,
            'total_images': len(images)
        }

    # Unable to use @accepts because the input files come in a form-data, not json.
    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',), resources=('diagnostic_imaging',))
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

        reporter, _ = token_auth.current_user()
        mi_schema = MedicalImagingSchema()
        hex_token = secrets.token_hex(4)

        images = []
        for i, img in enumerate(request.files.getlist('image')):
            mi_data = mi_schema.load(request.form)
            mi_data.user_id = user_id
            mi_data.reporter_id = reporter.user_id

            img = ImageUpload(img.stream, user_id, prefix='medical_images')
            img.allowed_types = ALLOWED_MEDICAL_IMAGE_TYPES
            img.max_size = MEDICAL_IMAGE_MAX_SIZE
            img.validate()
            img.save(f'{mi_data.image_type}_{mi_data.image_date}_{hex_token}_{i}.{img.extension}')
            mi_data.image_path = img.filename

            images.append(mi_data)

        if not images:
            # No images uploaded, still want to store rest of form data.
            mi_data = mi_schema.load(request.form)
            mi_data.user_id = user_id
            mi_data.reporter_id = reporter.user_id

            images.append(mi_data)

        db.session.add_all(images)
        db.session.commit()

    @ns.doc(params={'image_id': 'ID of the image to be deleted'})
    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',), resources=('diagnostic_imaging',))
    @responds(status_code=204, api=ns)
    def delete(self, user_id):
        idx = request.args.get('image_id', type=int)

        if not idx:
            raise BadRequest(f'Please provide an image ID.')

        data = MedicalImaging.query.filter_by(user_id=user_id, idx=idx).one_or_none()
        if not data:
            raise BadRequest(f'Image {idx} not found.')

        # ensure logged in user is the reporter for this image
        self.check_ehr_permissions(data)

        fd = FileDownload(user_id)
        fd.delete(data.image_path)

        db.session.delete(data)
        db.session.commit()


@ns.route('/bloodtest/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedBloodTest(BaseResource):
    
    # Multiple tests per user allowed
    __check_resource__ = False
    
    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',), resources=('blood_chemistry',))
    @accepts(schema=MedicalBloodTestsInputSchema, api=ns)
    @responds(schema=MedicalBloodTestSchema, status_code=201, api=ns)
    def post(self, user_id):
        """
        Resource to submit a new blood test instance for the specified client.

        Test submissions are given a test_id which can be used to reference back
        to the results related to this submission. Each submission may have 
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
            'notes': request.parsed_obj['notes'],
            'was_fasted': request.parsed_obj['was_fasted']
        })
        
        db.session.add(client_bt)
        db.session.commit()
        
        #for each provided result, evaluate the results based on the range that most applies to the client
        for result in results:
            ranges = LookupBloodTestRanges.query.filter_by(modobio_test_code=result['modobio_test_code'])
            client = User.query.filter_by(user_id=user_id).one_or_none()
            
            if ranges.count() > 1:
                
                #calculate client age
                today = date.today()
                client_age = today.year - client.dob.year
                if today.month < client.dob.month or (today.month == client.dob.month and today.day < client.dob.day):
                    client_age -= 1
                    
                #filter results by client age
                age_ranges = ranges.filter(and_(
                    or_(LookupBloodTestRanges.age_min <= client_age, LookupBloodTestRanges.age_min == None),
                    or_(LookupBloodTestRanges.age_max >= client_age, LookupBloodTestRanges.age_max == None)))

                #if age filtering narrowed results, record client age as a determining factor
                if ranges.count() > age_ranges.count():
                    result['age'] = client_age

                #filter results by client biological sex
                sex_ranges = age_ranges.filter(
                    or_(LookupBloodTestRanges.biological_sex_male == client.biological_sex_male,
                        LookupBloodTestRanges.biological_sex_male == None))

                #if biological sex filtering narrowed results, record client sex as a determining factor
                if age_ranges.count() > sex_ranges.count():
                    result['biological_sex_male'] = client.biological_sex_male

                #filter results by menstrual cycle if client bioligocal sex is female
                if not client.biological_sex_male:
                    client_cycle_row = ClientFertility.query.filter_by(user_id=user_id).order_by(ClientFertility.created_at.desc()).first()
                    if client_cycle_row == None or client_cycle_row.status == 'unknown':
                        #default if client has not submitted any fertility information
                        client_cycle = 'follicular phase'
                    else:
                        client_cycle = client_cycle_row.status
                        
                    relevant_cycles = []
                    for cycle in sex_ranges.all():
                        if cycle.menstrual_cycle:
                            relevant_cycles.append(cycle.menstrual_cycle)
                            
                    #some tests only care if the client is 'pregnant', 'not pregnant', or 'postmenopausal'
                    if 'pregnant' in relevant_cycles:
                        if client_cycle_row == None:
                            client_cycle = 'not pregnant'
                        else:
                            if client_cycle_row.status != 'postmenopausal':
                                client_cycle = client_cycle_row.pregnant
                            
                    if client_cycle in relevant_cycles:
                        cycle_ranges = sex_ranges.filter_by(menstrual_cycle=client_cycle)
                    else:
                        #if client cycle is not in one of the cycles that explicitely matters to this test
                        #type, only ranges with None as the menstrual cycle can be considered
                        cycle_ranges = sex_ranges.filter_by(menstrual_cycle=None)
                else:
                    cycle_ranges = sex_ranges

                #if menstrual cycle filtering narrowed results, record client cycle as a determining factor
                if sex_ranges.count() > cycle_ranges.count():
                    result['menstrual_cycle'] = client_cycle

                client_races = {}
                for id, name in db.session.query(ClientRaceAndEthnicity.race_id, LookupRaces.race_name) \
                    .filter(ClientRaceAndEthnicity.race_id == LookupRaces.race_id,
                            ClientRaceAndEthnicity.user_id == user_id).all():
                    client_races[id] = name
        
                #prune remaining ranges by races relevant to the client
                applicable_race = False
                race_ranges = []
                result['race'] = []
                for range in cycle_ranges.all():
                    if range.race_id:
                        if range.race_id in client_races:
                            applicable_race = True
                            race_ranges.append(range)
                            result['race'].append(client_races[range.race_id])
                            
                if not applicable_race:
                    #if the range had no races that were applicable to the client, only consider ranges
                    #with None as the race
                    race_ranges = cycle_ranges.filter_by(race_id=None).all()
                    
                #if race filtering narrowed results, record client race as a determining factor
                if cycle_ranges.count() > len(race_ranges):
                    result['race'] =', '.join(result['race'])

                if len(race_ranges) > 1:
                    """
                    If more than 1 range remains at this point, it is because the client has multiple
                    races that can impact the evaluation. In this case, we want the 'most conservative'
                    range. Meaning of all the remaining ranges, we want to take the highest min values
                    and lowest max values.
                    """
                    critical_min = ref_min = 0
                    critical_max = ref_max = float("inf")
                    races = []
                    for range in race_ranges:
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
                    'critical_min': race_ranges[0].critical_min,
                    'ref_min': race_ranges[0].ref_min,
                    'ref_max': race_ranges[0].ref_max,
                    'critical_max': race_ranges[0].critical_max
                }
            else:
                eval_values = {
                    'critical_min': ranges[0].critical_min,
                    'ref_min': ranges[0].ref_min,
                    'ref_max': ranges[0].ref_max,
                    'critical_max': ranges[0].critical_max
                }

            #fix ranges if any are null
            if eval_values['critical_min'] == None:
                eval_values['critical_min'] = 0
            if eval_values['ref_min'] == None:
                eval_values['ref_min'] = 0
            if eval_values['ref_max'] == None:
                eval_values['ref_max'] = float('inf')
            if eval_values['critical_max'] == None:
                eval_values['critical_max'] = float('inf')

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

    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',), resources=('blood_chemistry',))
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
        
@ns.route('/bloodtest/image/<int:user_id>/')
@ns.doc(params={'test_id': 'Test ID number'})
class MedBloodTestImage(BaseResource):
    
    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',), resources=('blood_chemistry',))
    @responds(schema=MedicalBloodTestSchema, api=ns, status_code=200)
    def patch(self, user_id):
        """
        This resource can be used to add an image to submitted blood test results.

        Args:
            image ([file]): image file to be added to test results (only .pdf files are supported, max size 20MB)
        """
        if not ('image' in request.files and request.files['image']):  
            raise BadRequest('No file selected.')
            
        test_id = request.args.get('test_id', type=int)
        test = MedicalBloodTests.query.filter_by(test_id=test_id).one_or_none()
        if not test:
            raise BadRequest(f'No test exists with test id {test_id} for the user with user_id {user_id}.')

        prev_image = test.image_path

        # add file to S3
        hex_token = secrets.token_hex(4)
        img = FileUpload(request.files['image'].stream, test.user_id, prefix='bloodtest')
        img.allowed_types = ('pdf',)
        img.max_size = MEDICAL_IMAGE_MAX_SIZE
        img.validate()
        img.save(f'test{test.test_id:05d}_{hex_token}.{img.extension}')
        
        # store file path in db
        test.image_path = img.filename
        db.session.commit()

        # Upload successful, delete previous
        if prev_image:
            fd = FileDownload(test.user_id)
            fd.delete(prev_image)


        reporter = User.query.filter_by(user_id=test.reporter_id).one_or_none()

        if test.reporter_id != user_id:
            reporter_pic = get_profile_pictures(test.reporter_id, True)            
        else:
            reporter_pic = get_profile_pictures(user_id, False)
        
        res = {
            'test_id': test.test_id,
            'user_id': test.user_id,
            'date': test.date,
            'notes': test.notes,
            'reporter_firstname': reporter.firstname,
            'reporter_lastname': reporter.lastname,
            'reporter_id': test.reporter_id,
            'reporter_profile_pictures': reporter_pic,
            'image': img.url() 
        }
        
        return res

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
        fd = FileDownload(user_id)
            
        for test in blood_tests:
            if test[0].image_path:
                image_path = fd.url(test[0].image_path)
            else:
                image_path = None
            
            if test[0].reporter_id != user_id:
                reporter_pic = get_profile_pictures(test[0].reporter_id, True)            
            else:
                reporter_pic = get_profile_pictures(user_id, False)
                    
            data = test[0].__dict__
            data.update(
                {'reporter_firstname': test[1],
                 'reporter_lastname': test[2],
                 'reporter_profile_pictures': reporter_pic,
                 'image': image_path})
            response.append(data)
        payload = {}
        payload['items'] = response
        payload['total'] = len(blood_tests)
        payload['user_id'] = user_id
        return payload

@ns.route('/bloodtest/results/<int:test_id>/')
@ns.doc(params={'test_id': 'Test ID number'})
@ns.deprecated
class MedBloodTestResults(BaseResource):
    """
    Resource for working with a single blood test 
    entry instance, test_id.

    Each test instance may have multiple test results. 

    DEPRECATED 9.15.22 v1.2.1
    """
    @token_auth.login_required(user_type=('client', 'provider'), resources=('blood_chemistry',))
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

        fd = FileDownload(results[0][0].user_id)
        if results[0][0].image_path:
            image_path = fd.url(results[0][0].image_path)
        else:
            image_path = None
            
            
        if results[0][0].reporter_id != results[0][0].user_id:
            reporter_pic = get_profile_pictures(results[0][0].reporter_id, True)            
        else:
            reporter_pic = get_profile_pictures(results[0][0].user_id, False)
                
        # prepare response with test details   
        nested_results = {'test_id': test_id, 
                          'date' : results[0][0].date,
                          'notes' : results[0][0].notes,
                          'image': image_path,
                          'reporter_id': results[0][0].reporter_id,
                          'reporter_firstname': results[0][3].firstname,
                          'reporter_lastname': results[0][3].lastname,
                          'reporter_profile_pictures': reporter_pic,
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


@ns.route('/bloodtest/results/search/<int:user_id>/')
@ns.doc(params={
    'test_id': 'Test ID number', 
    'start_date': 'Start date for date range', 
    'end_date': 'End date for date range',
    'modobio_test_code': 'Modobio test code',
    'page': 'page of paginated results',
    'per_page': 'results per page'})
class MedBloodTestResultsSearch(BaseResource):
    """
    Search for blood test results by test_id, date range, or modobio_test_code.

    This allows users to search for individual test results, batch entries, or both
    """
    @token_auth.login_required(user_type=('client', 'provider'), resources=('blood_chemistry',))
    @responds(schema=MedicalBloodTestResultsOutputSchema, api=ns)
    def get(self, user_id):
        """
        Returns details of the test denoted by test_id as well as 
        the actual results submitted.
        """
        modobio_test_code = request.args.get('modobio_test_code', type=str)
        test_id = request.args.get('test_id', type=int)
        start_date = request.args.get('start_date', type=date_validator)
        end_date =  request.args.get('end_date', type=date_validator)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)
        
        query =  db.session.query(
                MedicalBloodTests, MedicalBloodTestResults, User
                ).filter(
                    MedicalBloodTestResults.test_id == MedicalBloodTests.test_id,
                    User.user_id == MedicalBloodTests.reporter_id,
                    MedicalBloodTests.user_id==user_id
                )
        
        if test_id:
            query = query.filter(MedicalBloodTests.test_id==test_id)
        if modobio_test_code:
            query = query.filter(MedicalBloodTestResults.modobio_test_code==modobio_test_code)
        if start_date:
            query = query.filter(MedicalBloodTests.date >= start_date)
        if end_date:
            query = query.filter(MedicalBloodTests.date <= end_date)

        # order the query by date descending
        query = query.order_by(MedicalBloodTests.date.desc())

        results = query.paginate(page=page, per_page=per_page, error_out=False)
        
        if not results:
            return

        test_results = {} # key is test_id, value is list of test results
        reporter_pics = {} # key is reporter_id, value is list of profile pictures
        for test, test_result, reporter in results.items:
            # group results by test_id
            test_id = test.test_id
            if test_id in test_results:
                test_results[test_id]['results'].append( {
                    'modobio_test_code': test_result.test_type.modobio_test_code, 
                    'result_value': test_result.result_value,
                    'evaluation': test_result.evaluation,
                    'age': test_result.age,
                    'biological_sex_male': test_result.biological_sex_male,
                    'race': test_result.race,
                    'menstrual_cycle': test_result.menstrual_cycle
                })
            else:
                # bring up test image
                fd = FileDownload(test.user_id)
                if test.image_path:
                    image_path = fd.url(test_result.image_path)
                else:
                    image_path = None
            
                if test.reporter_id != user_id:
                    reporter_id = test.reporter_id
                    if test.reporter_id not in reporter_pics:
                        reporter_pics[reporter_id] = get_profile_pictures(reporter_id, True)
                else:
                    reporter_id = user_id
                    if reporter_id not in reporter_pics:
                        reporter_pics[test.user_id] = get_profile_pictures(reporter_id, False)
                        
                test_results[test_id] = {
                    'test_id': test_id, 
                    'date' : test.date,
                    'notes' : test.notes,
                    'results': [{
                                    'modobio_test_code': test_result.test_type.modobio_test_code, 
                                    're+sult_value': test_result.result_value,
                                    'evaluation': test_result.evaluation,
                                    'age': test_result.age,
                                    'biological_sex_male': test_result.biological_sex_male,
                                    'race': test_result.race,
                                    'menstrual_cycle': test_result.menstrual_cycle
                                }], 
                    'image': image_path,
                    'reporter_id': test.reporter_id,
                    'reporter_firstname': reporter.firstname,
                    'reporter_lastname': reporter.lastname,
                    'reporter_profile_pictures': reporter_pics[reporter_id],
                    'was_fasted': test.was_fasted}

        
        # remove page from query parameters so as to not conflict with pagination links
        _args = request.args.to_dict()
        _args.pop('page', None)

        payload = {}
        payload['items'] = list(test_results.values())
        payload['tests'] = len(test_results)
        payload['test_results'] = len(results.items)
        payload['user_id'] = user_id
        payload["_links"] =   {
            '_prev': url_for('api.doctor_med_blood_test_results_search', user_id = user_id, page=results.prev_num,**_args, _external = True) if results.has_prev else None,
            '_next': url_for('api.doctor_med_blood_test_results_search', user_id = user_id, page=results.next_num,**_args, _external = True) if results.has_next else None,
        }
        return payload



@ns.route('/bloodtest/results/all/<int:user_id>/')
@ns.doc(params={'user_id': 'Client ID number'})
class AllMedBloodTestResults(BaseResource):
    """
    Endpoint for returning all blood test results from a client.

    This includes all test submisison details along with the test
    results associated with each test submission. 
    """
    @token_auth.login_required(user_type=('client', 'provider'), resources=('blood_chemistry',))
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

        test_ids = set([(x[0].test_id, x[0].reporter_id, x[3].firstname, x[3].lastname, x[0].image_path, x[0].was_fasted) for x in results])
        nested_results = [
            {
                'test_id': x[0], 
                'was_fasted': x[5],
                'reporter_id': x[1], 
                'reporter_firstname': x[2], 
                'reporter_lastname': x[3], 
                'image': x[4], 
                'results': []} for x in test_ids ]
        
        # loop through results in order to nest results in their respective test
        # entry instances (test_id)
        fd = FileDownload(user_id)
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
                        # get presigned s3 link if present
                        image_path = test.get('image')
                        if image_path:
                            test['image'] = fd.url(image_path)

                #retrieve reporter profile pic
                if test['reporter_id'] != user_id:
                    reporter_pic = get_profile_pictures(test['reporter_id'], True)            
                else:
                    reporter_pic = get_profile_pictures(user_id, False)
                test['reporter_profile_pictures'] = reporter_pic
                                
        payload = {}
        payload['items'] = nested_results
        payload['tests'] = len(test_ids)
        payload['test_results'] = len(results)
        payload['user_id'] = user_id
        return payload


@ns.route('/medicalhistory/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
@ns.deprecated
class MedHistory(BaseResource):
    @token_auth.login_required(user_type=('client', 'provider'),)
    @responds(schema=MedicalHistorySchema, api=ns)
    def get(self, user_id):
        """returns client's medical history as a json for the user_id specified"""
        self.check_user(user_id, user_type='client')

        client = MedicalHistory.query.filter_by(user_id=user_id).first()
        return client

    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',))
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

    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',))
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
    @token_auth.login_required(user_type=('client', 'provider'), resources=('general_medical_info',))
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

    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',), resources=('general_medical_info',))
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
    @token_auth.login_required()
    @responds(schema=MedicalInstitutionsSchema(many=True), api=ns)
    def get(self):
        """returns all medical institutes currently in the database"""

        institutes = MedicalInstitutions.query.all()
        
        return institutes

@ns.route('/medicalinstitutions/recordid/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class ExternalMedicalRecordIDs(BaseResource):
    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',))
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

    @token_auth.login_required(user_type=('client', 'provider'),)
    @responds(schema=MedicalExternalMREntrySchema, api=ns)
    def get(self, user_id):
        """returns all medical record ids for user_id"""
        self.check_user(user_id, user_type='client')

        client_med_record_ids = MedicalExternalMR.query.filter_by(user_id=user_id).all()

        return client_med_record_ids


@ns.route('/surgery/<int:user_id>/')
@ns.doc(params={'user_id': 'Client user ID number'})
class MedicalSurgeriesAPI(BaseResource):

    @token_auth.login_required(user_type=('client', 'provider'), staff_role=('medical_doctor',), resources=('general_medical_info',))
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

    @token_auth.login_required(user_type=('client', 'provider'), resources=('general_medical_info',))
    @responds(schema=MedicalSurgeriesSchema(many=True), api=ns)
    def get(self, user_id):
        """returns a list of all surgeries for the given user_id"""
        self.check_user(user_id, user_type='client')

        return MedicalSurgeries.query.filter_by(user_id=user_id).all()

