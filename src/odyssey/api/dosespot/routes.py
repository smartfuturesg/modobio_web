import requests
from datetime import datetime

from flask import g, request, current_app
from flask_accepts import accepts, responds
from flask.json import dumps
from flask_restx import Resource, Namespace
from sqlalchemy import select
from werkzeug.exceptions import BadRequest

from odyssey import db

from odyssey.api.dosespot.models import (
    DoseSpotPractitionerID,
    DoseSpotPatientID,
    DoseSpotProxyID
)
from odyssey.api.dosespot.schemas import (
    DoseSpotPrescribeSSO,
    DoseSpotPharmacyNestedSelect,
    DoseSpotEnrollmentGET,
    DoseSpotAllergyOutput,
    DoseSpotPrescribedOutput
)
from odyssey.api.lookup.models import (
    LookupTerritoriesOfOperations,
)

from odyssey.api.notifications.models import Notifications

from odyssey.api.user.models import User
from odyssey.integrations.dosespot import DoseSpot
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource

ns = Namespace('dosespot', description='Operations related to DoseSpot')

@ns.route('/allergies/<int:user_id>/')
class DoseSpotAllergies(BaseResource):
    @token_auth.login_required(user_type=('staff','client'), resources=('general_medical_info',))
    @responds(schema=DoseSpotAllergyOutput,status_code=200,api=ns)
    def get(self, user_id):
        """
        Bring up the client's allergies to medications stored on DoseSpot
        """
        ds_patient = DoseSpotPatientID.query.filter_by(user_id=user_id).one_or_none()
        ds = DoseSpot()
        if not ds_patient:
            raise BadRequest("User not registered with DoseSpot. User missing required address details")

        ds_allergies = ds.allergies(user_id)
        
        payload = {'items': ds_allergies['Items'],
                   'total_items': len(ds_allergies['Items'])}

        return payload

@ns.route('/create-practitioner/<int:user_id>/')
class DoseSpotPractitionerCreation(BaseResource):
    @token_auth.login_required(user_type=('staff',),staff_role=('medical_doctor',))
    @responds(status_code=201, api=ns)
    def post(self, user_id):
        """
        POST - Only a DoseSpot Admin will be able to use this endpoint. As a workaround
               we have stored a DoseSpot Admin credentials so the ModoBio system will be able
               to create the practitioner on the DoseSpot platform
        """
        ds = DoseSpot()
        ds.onboard_practitioner(user_id)
        db.session.commit()
        return 

@ns.route('/prescribe/<int:user_id>/')
class DoseSpotPatientCreation(BaseResource):
    @token_auth.login_required(user_type=('staff','client'), resources=('medications',))
    @responds(schema=DoseSpotPrescribedOutput,status_code=200,api=ns)
    def get(self, user_id):
        """
        Returns the client's prescriptions that have been prescribed through DoseSpot. Both client and medical doctor practitioners have access 
        to this endpoint. 

        Parameters
        ----------
        user_id : int
            user_id for the client
        """
        ds = DoseSpot()
        prescriptions = ds.prescriptions(user_id)

        payload = {'items': prescriptions['Items'],
                   'total_items': len(prescriptions['Items'])}

        return payload

    @token_auth.login_required(user_type=('staff',),staff_role=('medical_doctor',), resources=('medications',))      
    @responds(schema=DoseSpotPrescribeSSO,status_code=201,api=ns)
    def post(self, user_id):
        """
        Generate an SSO directed at the prescribing page on the DoseSpot platform. Only practitioners with the medical_doctor role will 
        have access to this endpoint. 
        TODO: restrict this endpoint to practitioners given care team access to the user in the path parameter

        Parameters
        ----------
        user_id : int
            user_id for the client
        
        Returns
        -------
        url : str
            SSO to the DoseSpot prescribing portal
        """
        curr_user,_ = token_auth.current_user()

        ds = DoseSpot(practitioner_user_id = curr_user.user_id)
        
        return {'url': ds.prescribe(client_user_id = user_id)}

@ns.route('/notifications/<int:user_id>/')
class DoseSpotNotificationSSO(BaseResource):
    @token_auth.login_required(user_type=('staff_self',),staff_role=('medical_doctor',))
    @responds(schema=DoseSpotPrescribeSSO,status_code=200, api=ns)
    def get(self, user_id):
        """
        Bring up DoseSpot notifications for the practitioner. Stores notification count as a notification 
        entry on the modobio platform. Responds with SSO to access notification content on DoseSpot. 

        Parameters
        ----------
        user_id : int
            Must be a practitioner registered with DoseSpot
        
        Returns
        -------
        url : str
            SSO which sends user directly to their notifications
        """
        ds = DoseSpot(practitioner_user_id = user_id)
        url = ds.notifications(user_id)

        return {'url': url}

@ns.route('/enrollment-status/<int:user_id>/')
@ns.doc(params={'user_type': '\'client\' or \'staff\'. defaults to staff'})
class DoseSpotEnrollmentStatus(BaseResource):
    @token_auth.login_required(user_type=('staff','client'),staff_role=('medical_doctor',))
    @responds(schema=DoseSpotEnrollmentGET,status_code=200, api=ns)
    def get(self, user_id):
        """
        Returns the DoseSpot enrollment status for the provided user_id. Responds in error if the user is not enrolled at all. 

        Parameters
        ----------
        user_id : int
            Must be a practitioner registered with DoseSpot
        
        Returns
        -------
        enrollment status : str
            'enrolled', 'pending', 'not enrolled' (client only) 
        """
        ds = DoseSpot()
        utype = request.args.get('user_type', 'staff', type = str)
        return {'status':ds.enrollment_status(user_id, user_type = utype)}

@ns.route('/select/pharmacies/<int:user_id>/')
@ns.doc(params = {'zipcode': '(optional) overrides user\'s zipcode', 
            'territory_id': '(optional) overrides user\'s state'})
class DoseSpotSelectPharmacies(BaseResource):
    @token_auth.login_required(user_type=('client',))
    def get(self,user_id):
        """
        Queries DoseSpot for a list of available pharmacies. By default this endpoint uses the client's address
        to locate pharmacies. Optionally a user may submit a zipcode and territory_id 

        Parameters
        ----------
        user_id : int
            User ID

        zipcode : str
            Optional zipcode for pharmacy search

        territory_id : int
            Optional territory_id from LookupTerritoriesOfOperations

        Returns
        -------
        list(dict)
            list of pharmacies
        """
        zipcode = request.args.get('zipcode', None)
        territory_id = request.args.get('territory_id', None)

        # if no zipcode not state specified, use client's address detail by default
        if not zipcode and not territory_id:
            user = User.query.filter_by(user_id = user_id).one_or_none()
            zipcode = user.client_info.zipcode
            territory_id = user.client_info.territory_id
        
        ds = DoseSpot()

        pharmacies = ds.pharmacy_search(territory_id = territory_id, zipcode = zipcode)
        
        return pharmacies['Items']

@ns.route('/pharmacies/<int:user_id>/')
class DoseSpotPatientPharmacies(BaseResource):
    @token_auth.login_required(user_type=('client','staff'), staff_role=('medical_doctor',))
    def get(self, user_id):
        """
        Retrieve from DoseSpot the pharmacies the Modobio client has selected (at most 3.)
        Parameters
        ----------
        user_id : int
            User ID

        Returns
        -------
        list(dict)
            list of up to 3 pharmacies
        """
        
        ds = DoseSpot()
        pharmacies = ds.client_pharmacies(user_id)
        
        return pharmacies['Items']

    @token_auth.login_required(user_type=('client',))
    @accepts(schema=DoseSpotPharmacyNestedSelect,api=ns)
    @responds(status_code=201,api=ns)
    def post(self, user_id):
        """
        POST - The pharmacies the Modobio client has selected (at most 3.)
               We delete the existing pharmacy selection, and populate with the selected choices
               DoseSpot Admin credentials will be used for this endpoint
        """
        payload = request.json
        if len(payload['items'])>3:
            raise BadRequest('Can only select up to 3 pharmacies.')

        primary_pharm_count = 0
        for item in payload['items']:
            if item['primary_pharm']:
                primary_pharm_count+=1
            if primary_pharm_count > 1:
                raise BadRequest('Must select only 1 pharmacy to be set as primary.')
        if primary_pharm_count == 0:
            raise BadRequest('Must select 1 pharmacy to be set as primary.')


        ds = DoseSpot()

        ds.pharmacy_select(user_id, payload['items'])

        return