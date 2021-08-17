import os, boto3, secrets, pathlib
from datetime import datetime
from dateutil.relativedelta import relativedelta

from flask import g, request, current_app
from flask_accepts import accepts, responds
from flask_restx import Resource, Namespace

from odyssey import db

from odyssey.api.user.models import User

from odyssey.utils.auth import token_auth

from odyssey.utils.errors import (
    UserNotFound, 
    IllegalSetting, 
    ContentNotFound,
    InputError,
    MedicalConditionAlreadySubmitted,
    GenericNotFound,
    UnauthorizedUser
)
from odyssey.utils.misc import check_client_existence, check_blood_test_existence, check_blood_test_result_type_existence, check_medical_condition_existence

from odyssey.utils.base.resources import BaseResource

ns = Namespace('dosespot', description='Operations related to DoseSpot')

@ns.route('/create-practioner/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class MedBloodPressures(BaseResource):
    @token_auth.login_required(resources=('blood_pressure',))
    @responds(schema=MedicalBloodPressuresOutputSchema, api=ns)
    def get(self, user_id):
        '''
        This request gets the users submitted blood pressure if it exists
        '''
        super().check_user(user_id, user_type='client')
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
        POST to create a practitioner on DoseSpot platform
        '''
        # First check if the client exists
        super().check_user(user_id, user_type='client')
        super().set_reporter_id(request.parsed_obj)

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
        super().check_user(user_id, user_type='client')

        idx = request.args.get('idx', type=int)
        if idx:
            result = MedicalBloodPressures.query.filter_by(user_id=user_id, idx=idx).one_or_none()
            if not result:
                raise GenericNotFound(f"The blood pressure result with user_id {user_id} and idx {idx} does not exist.")
                
            #ensure logged in user is the reporter for this pressure reasing
            super().check_ehr_permissions(result)

            db.session.delete(result)
            db.session.commit()
        else:
            raise InputError(message="idx must be an integer.")