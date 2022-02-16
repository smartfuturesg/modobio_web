import logging
logger = logging.getLogger(__name__)

from flask import request
from flask_accepts import responds, accepts
from flask_restx import Namespace
from sqlalchemy import select
from werkzeug.exceptions import BadRequest

from odyssey import db
from odyssey.api.lookup.models import LookupCountriesOfOperations, LookupCurrencies
from odyssey.api.system.models import SystemTelehealthSessionCosts, SystemVariables
from odyssey.api.system.schemas import SystemTelehealthSettingsSchema
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource
from odyssey.utils.misc import delete_user

ns = Namespace('system', description='Endpoints for system admin functions.')

@ns.route('/telehealth-settings/')
class SystemTelehealthSettingsApi(BaseResource):
    """ Endpoints related to system telehealth settings.
    """

    @token_auth.login_required()
    @responds(schema=SystemTelehealthSettingsSchema,status_code=200, api=ns)
    def get(self):
        costs = db.session.execute(
            select(SystemTelehealthSessionCosts, LookupCurrencies).
            join(LookupCurrencies, LookupCurrencies.idx == SystemTelehealthSessionCosts.currency_id)).all()

        practitioner_rates = LookupCurrencies.query.one_or_none()
        formatted_costs = []
        #TODO: Will we take this out?
        for cost, lookup in costs:
            cost.country = lookup.country
            cost.currency_symbol_and_code = lookup.symbol_and_code
            cost.session_min_cost = practitioner_rates.min_rate
            cost.session_max_cost = practitioner_rates.max_rate
            cost.session_cost = 100.00 # TODO, this is useless now, but will be kept for a few more stories 10/11/2021
            formatted_costs.append(cost)

        session_duration = int(SystemVariables.query.filter_by(var_name='Session Duration').one_or_none().var_value)
        booking_notice_window = int(SystemVariables.query.filter_by(var_name='Booking Notice Window').one_or_none().var_value)
        confirmation_window = float(SystemVariables.query.filter_by(var_name='Confirmation Window').one_or_none().var_value)
        res = {'costs': formatted_costs,
                'session_duration': session_duration,
                'booking_notice_window': booking_notice_window,
                'confirmation_window': confirmation_window}
        return res

    @token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
    @accepts(schema=SystemTelehealthSettingsSchema, api=ns)
    # @responds(schema=SystemTelehealthSettingsSchema, status_code=201, api=ns)
    @ns.deprecated
    def put(self):
        """
        This endpoint is temporarily disabled until further security measures are established
        """
        return 'This endpoint is disabled until further notice.', 403

        res = {'costs': []}
        for cost in request.parsed_obj['costs']:
            #if a cost for this currency/profession combination does not exist, it is invalid
            exists = SystemTelehealthSessionCosts.query.filter_by(profession_type=cost.profession_type, currency_id=cost.currency_id).one_or_none()
            if exists:
                data = cost.__dict__
                del data['_sa_instance_state']
                exists.update(data)
                exists.session_cost = str(exists.session_cost)          
                res['costs'].append(exists)
            else:
                raise BadRequest(
                    f'No cost found for currency {cost.currency_id} '
                    f'and profession {cost.profession_type}.')

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


@ns.route('/delete-user/<int:user_id>/')
class SystemDeleteUserApi(BaseResource):
    """
    Endpoint for the system admin to delete a user
    """
    
    @token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
    @ns.doc(params={'delete_type': "Denotes what portion of the user should be deleted. Can be 'client','staff', or 'both "})
    @responds(status_code=204, api=ns)
    def delete(self, user_id):
        """
        This endpoint can be used to instantly delete a user by the system admin. Note that unlike the
        self-deletion process that a user can initiate, this does not have the step of the user being
        makred as 'closed' for 30 days before being deleted by the automated system.
        
        The system admin should specify which portion of the user's account should be deleted by supplying 
        either 'client', 'staff', or 'both' in the delete_type arg
        """
        delete_type = request.args.get('delete_type', type=str)
        if delete_type not in ('client', 'staff', 'both'):
            raise BadRequest('Invalid delete type specified.')
        delete_user(user_id, token_auth.current_user()[0].user_id, delete_type)
        
        return {'message': f'User with id {user_id} has been removed with a delete_type of {delete_type}.'}           