from flask import request
from flask_accepts import responds, accepts
from flask_restx import Resource

from odyssey.api import api

from odyssey.utils.auth import token_auth
from odyssey.api.system.models import SystemTelehealthSessionCosts, SystemVariables
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

        session_duration = int(SystemVariables.query.filter_by(var_name='Session Duration').one_or_none().var_value)
        booking_notice_window = int(SystemVariables.query.filter_by(var_name='Booking Notice Window').one_or_none().var_value)
        confirmation_window = float(SystemVariables.query.filter_by(var_name='Confirmation Window').one_or_none().var_value)

        res = {'costs': costs,
                'session_duration': session_duration,
                'booking_notice_window': booking_notice_window,
                'confirmation_window': confirmation_window}
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
                
        #update session variables
        if 'session_duration' in request.parsed_obj:
            ses_dur = SystemVariables.query.filter_by(var_name='Session Duration').one_or_none()
            ses_dur.update({'var_value': str(request.parsed_obj['session_duration'])})
        if 'booking_notice_window' in request.parsed_obj:
            book_window = SystemVariables.query.filter_by(var_name='Booking Notice Window').one_or_none()
            book_window.update({'var_value': str(request.parsed_obj['booking_notice_window'])})
        if 'confirmation_window' in request.parsed_obj:
            con_window = SystemVariables.query.filter_by(var_name='Confirmation Window').one_or_none()
            con_window.update({'var_value': str(request.parsed_obj['confirmation_window'])})

        db.session.commit()
        return request.parsed_obj