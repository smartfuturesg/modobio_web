from flask import request
from flask_accepts import responds, accepts
from flask_restx import Resource

from odyssey.api import api
from odyssey.defaults import TELEHEALTH_BOOKING_NOTICE_WINDOW, TELEHEALTH_SESSION_DURATION, TELEHEALTH_CONFIRMATION_WINDOW

from odyssey.utils.auth import token_auth
from odyssey.api.system.models import SystemTelehealthSessionCosts
from odyssey.api.system.schemas import SystemTelehealthSettingsSchema
from odyssey.api.lookup.models import LookupCountriesOfOperations

from odyssey import db

ns = api.namespace('system', description='Endpoints for system functions.')


@ns.route('/telehealth-settings/')
class SystemTelehealthSettingsApi(Resource):
    """ Endpoints related to system telehealth settings.
    """

    @token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
    @responds(schema=SystemTelehealthSettingsSchema,status_code=200, api=ns)
    def get(self):
        costs = SystemTelehealthSessionCosts.query.all()
        for cost in costs:
            cost.territory_name = LookupCountriesOfOperations.query.filter_by(idx=cost.territory_id).one_or_none().country

        res = {'costs': costs,
                'session_duration': TELEHEALTH_SESSION_DURATION,
                'booking_notice_window': TELEHEALTH_BOOKING_NOTICE_WINDOW,
                'confirmation_window': TELEHEALTH_CONFIRMATION_WINDOW}
        return res

    @token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
    @accepts(schema=SystemTelehealthSettingsSchema, api=ns)
    @responds(schema=SystemTelehealthSettingsSchema, status_code=201, api=ns)
    def put(self):
        for cost in request.parsed_obj['costs']:
            #check if this profession/territory combination already exists
            #if yes, update. if no, add
            exists = SystemTelehealthSessionCosts.query.filter_by(profession_type=cost.profession_type, territory_id=cost.territory_id).one_or_none()
            if exists:
                data = cost.__dict__
                del data['_sa_instance_state']
                exists.update(data)
            else:
                db.session.add(cost)
                
        db.session.commit()

        #update session variables
        if 'session_duration' in request.parsed_obj:
            TELEHEALTH_SESSION_DURATION = request.parsed_obj['session_duration']
        if 'booking_notice_window' in request.parsed_obj:
            TELEHEALTH_BOOKING_NOTICE_WINDOW = request.parsed_obj['booking_notice_window']
        if 'confirmation_window' in request.parsed_obj:
            TELEHEALTH_CONFIRMATION_WINDOW = request.parsed_obj['confirmation_window']

        return request.parsed_obj