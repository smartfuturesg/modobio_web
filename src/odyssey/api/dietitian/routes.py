import logging

from flask import request, current_app
from flask_accepts import accepts, responds
from flask_restx import Namespace
from sqlalchemy import select
from werkzeug.exceptions import BadRequest, Unauthorized

from odyssey import db

from odyssey.utils.auth import token_auth

from odyssey.api.doctor.schemas import (
    MedicalCredentialsSchema,
    MedicalCredentialsInputSchema,
)
from odyssey.api.staff.models import StaffRoles
from odyssey.api.practitioner.models import PractitionerCredentials
from odyssey.utils.base.resources import BaseResource

logger = logging.getLogger(__name__)

ns = Namespace('dietitian', description='Operations related to dietitian')

@ns.route('/credentials/<int:user_id>/')
class DietitianMedicalCredentialsEndpoint(BaseResource):
    @token_auth.login_required(user_type=('staff',),staff_role=('dietitian',))
    @responds(schema=MedicalCredentialsInputSchema,status_code=200,api=ns)
    def get(self, user_id):
        """
        GET Request for Pulling Medical Credentials for a practitioner

        User should be client
        """

        if not user_id:
            raise BadRequest('Missing User ID.')

        current_user, _ = token_auth.current_user()
        if current_user.user_id != user_id:
            raise Unauthorized()

        query = db.session.execute(
            select(PractitionerCredentials).
            where(
                PractitionerCredentials.user_id == user_id
                )
        ).scalars().all()
        return {'items': query}

    @token_auth.login_required(user_type=('staff',),staff_role=('dietitian',))
    @accepts(schema=MedicalCredentialsInputSchema, api=ns)
    @responds(status_code=201,api=ns)
    def post(self, user_id):
        """
        POST Request for submitting Medical Credentials for a practitioner

        User should be Staff Self
        """

        if not user_id:
            raise BadRequest('Missing User ID.')

        current_user, _ = token_auth.current_user()
        if current_user.user_id != user_id:
            raise Unauthorized()

        payload = request.parsed_obj
        curr_role = StaffRoles.query.filter_by(user_id=user_id,role='dietitian').one_or_none()
        state_check = {}
        for cred in payload['items']:
            # This takes care of ensuring credential number is submitted if user
            # submits a payload with a state for DEA and Medical License credential types
            if (cred.credential_type != 'npi' and cred.state) and not cred.credentials:
                raise BadRequest('Credential number is mandatory if submitting with a state.')

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

            cred.status = 'Pending Verification' if not any([current_app.config['DEV'],current_app.config['TESTING']]) else 'Verified'
            cred.role_id = curr_role.idx
            cred.user_id = user_id
            db.session.add(cred)

        db.session.commit()
        return

    @token_auth.login_required(user_type=('staff',),staff_role=('dietitian',))
    @accepts(schema=MedicalCredentialsSchema, api=ns)
    @responds(status_code=201,api=ns)
    def put(self, user_id):
        """
        PUT Request for updating the status for medical credentials

        User for this request should be the Staff Admin
        """

        if not user_id:
            raise BadRequest('Missing User ID.')

        current_user, _ = token_auth.current_user()
        if current_user.user_id != user_id:
            raise Unauthorized()
        
        valid_statuses = ['Rejected', 'Expired']

        payload = request.json
        
        curr_credentials = PractitionerCredentials.query.filter_by(user_id=user_id,idx=payload['idx']).one_or_none()
        if curr_credentials.status not in valid_statuses:
            raise BadRequest('Current credential status must be rejected or expired.')

        if curr_credentials:
            payload['status'] = 'Pending Verification'
            curr_credentials.update(payload)
            db.session.commit()
        else:
            raise BadRequest('Credentials not found.')
        return

    @token_auth.login_required(user_type=('staff',),staff_role=('dietitian',))
    @accepts(schema=MedicalCredentialsSchema(exclude=('status','credential_type','expiration_date','state','want_to_practice','credentials','country_id')),api=ns)
    @responds(status_code=201,api=ns)
    def delete(self, user_id):
        """
        DELETE Request for deleting medical credentials

        User for this request should be the Staff Self and Staff Admin
        """
        if not user_id:
            raise BadRequest('Missing User ID.')

        current_user, _ = token_auth.current_user()
        if current_user.user_id != user_id:
            raise Unauthorized()

        payload = request.json
        
        curr_credentials = PractitionerCredentials.query.filter_by(user_id=user_id,idx=payload['idx']).one_or_none()
        if curr_credentials:
            db.session.delete(curr_credentials)
            db.session.commit()
        else:
            raise BadRequest('Credentials not found.')
        return