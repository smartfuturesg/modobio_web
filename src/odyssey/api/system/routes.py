from flask import request
from flask_accepts import responds, accepts
from flask_restx import Resource

from odyssey.api import api

from odyssey.utils.auth import token_auth
from odyssey.utils.errors import GenericNotFound, DisabledEndpoint
from odyssey.api.system.models import SystemTelehealthSessionCosts, SystemVariables
from odyssey.api.system.schemas import SystemTelehealthSettingsSchema
from odyssey.api.lookup.models import LookupCountriesOfOperations, LookupCurrencyTypes

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
        #fill in data from lookup table and cast decimals to string so they are json serializable
        for cost in costs:
            cost.session_cost = str(cost.session_cost)
            cost.session_min_cost = str(cost.session_min_cost)
            cost.session_max_cost = str(cost.session_max_cost)
            cost_data = LookupCurrencyTypes.query.filter_by(idx=cost.currency_id).one_or_none()
            cost.country = cost_data.country
            cost.currency_symbol_and_code = cost_data.symbol_and_code

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
        """
        This endpoint is temporarily disabled until further security measures are established
        """
        raise DisabledEndpoint 

        res = {'costs': []}
        for cost in request.parsed_obj['costs']:
            #if a cost for this currency/profession combination does not exist, it is invalid
            exists = SystemTelehealthSessionCosts.query.filter_by(profession_type=cost.profession_type, currency_id=cost.currency_id).one_or_none()
            if exists:
                data = cost.__dict__
                del data['_sa_instance_state']
                exists.update(data)
                exists.session_cost = str(exists.session_cost)
                exists.session_min_cost = str(exists.session_min_cost)
                exists.session_max_cost = str(exists.session_max_cost)                
                res['costs'].append(exists)
            else:
                raise GenericNotFound('No cost exists for ' + cost.country + ' ' + cost.currency_symbol_and_code)
                
        #update session variables
        if 'session_duration' in request.parsed_obj:
            ses_dur = SystemVariables.query.filter_by(var_name='Session Duration').one_or_none()
            ses_dur.update({'var_value': str(request.parsed_obj['session_duration'])})
            res['session_duration'] = ses_dur.var_value
        if 'booking_notice_window' in request.parsed_obj:
            book_window = SystemVariables.query.filter_by(var_name='Booking Notice Window').one_or_none()
            book_window.update({'var_value': str(request.parsed_obj['booking_notice_window'])})
            res['booking_notice_window'] = book_window.var_value
        if 'confirmation_window' in request.parsed_obj:
            con_window = SystemVariables.query.filter_by(var_name='Confirmation Window').one_or_none()
            con_window.update({'var_value': str(request.parsed_obj['confirmation_window'])})
            res['confirmation_winow'] = con_window.var_value

        db.session.commit()
        return res