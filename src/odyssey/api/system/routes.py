from flask_accepts import responds, accepts
from flask_restx import Resource

from odyssey.api import api
from odyssey.defaults import TELEHEALTH_BOOKING_NOTICE_WINDOW, TELEHEALTH_SESSION_DURATION

from odyssey.utils.auth import token_auth
from odyssey.api.system.models import SystemTelehealthSessionCosts
from odyssey.api.system.schemas import SystemTelehealthSettingsSchema

from odyssey import db

ns = api.namespace('system', description='Endpoints for system functions.')


@ns.route('/teleheath-settings/')
class SystemTelehealthSettingsApi(Resource):
    """ Endpoints related to system telehealth settings.
    """

    @token_auth.login_required
    @responds(schema=SystemTelehealthSettingsSchema,status_code=200, api=ns)
    def get(self):
        costs = SystemTelehealthSessionCosts.query.all()
        res = {'costs': costs,
                'session_duration': TELEHEALTH_SESSION_DURATION,
                'booking_notice_window': TELEHEALTH_BOOKING_NOTICE_WINDOW}
        return res

    @token_auth.login_required
    @accepts(schema=SystemTelehealthSettingsSchema)
    @responds(schema=SystemTelehealthSettingsSchema, status_code=201, api=ns)
    def put(self):
        for cost in response.parsed_obj.costs:
            db.session.add(cost)
        db.session.commit()

        #update session variables
        TELEHEALTH_SESSION_DURATION = response.parsed_obj.session_duration
        TELEHEALTH_BOOKING_NOTICE_WINDOW = response.parsed_obj.booking_notice_window

        return response.parsed_obj