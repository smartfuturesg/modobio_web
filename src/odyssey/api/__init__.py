import logging
logger = logging.getLogger(__name__)

# Temporary workaround
# Flask 2.1 updated dependency werkzeug to 2.2. But flask-restx 0.5.1 uses a
# function from werkzeug 2.1 which was removed (it was internal anyway
# and should never have been used).
# Code copied from werkzeug v2.1.2. Remove on next update of flask-restx.
import werkzeug.routing
if not hasattr(werkzeug.routing, 'parse_rule'):
    import re
    _rule_re = re.compile(
        r"""
        (?P<static>[^<]*)                           # static rule data
        <
        (?:
            (?P<converter>[a-zA-Z_][a-zA-Z0-9_]*)   # converter name
            (?:\((?P<args>.*?)\))?                  # converter arguments
            \:                                      # variable delimiter
        )?
        (?P<variable>[a-zA-Z_][a-zA-Z0-9_]*)        # variable name
        >
        """,
        re.VERBOSE,
    )

    def _parse_rule(rule: str):
        """Parse a rule and return it as generator. Each iteration yields tuples
        in the form ``(converter, arguments, variable)``. If the converter is
        `None` it's a static url part, otherwise it's a dynamic one.
        :internal:
        """
        pos = 0
        end = len(rule)
        do_match = _rule_re.match
        used_names = set()
        while pos < end:
            m = do_match(rule, pos)
            if m is None:
                break
            data = m.groupdict()
            if data["static"]:
                yield None, None, data["static"]
            variable = data["variable"]
            converter = data["converter"] or "default"
            if variable in used_names:
                raise ValueError(f"variable name {variable!r} used twice.")
            used_names.add(variable)
            yield converter, data["args"] or None, variable
            pos = m.end()
        if pos < end:
            remaining = rule[pos:]
            if ">" in remaining or "<" in remaining:
                raise ValueError(f"malformed url rule: {rule!r}")
            yield None, None, remaining

    werkzeug.routing.parse_rule = _parse_rule

from flask import Blueprint
from flask_restx import Api

# To use authentication in Swagger:
# 1. Click Authenticate button at top of the page
# 2. Log in with name and password, leave apikey blank
# 3. Open tokens > POST /tokens/staff/
# 4. Click Try It Out
# 5. Click Execute
# 6. Copy 'token' from reponse
# 7. Back to top Authenticate button
# 8. In apikey field type: Bearer <paste token>
#
# There is a bit of a misnomer going on. We use authentication of type "apiKey",
# but technically it is not apiKey. apiKey is supposed to use a private http header,
# X-whatever. The authorization backend then looks for that header in requests.
#
# But instead our authorization backend listens for "Authorization: Bearer <key>".
# That is called the bearer (or token) authorization scheme. That scheme only
# exists in Swagger/OpenAPI version 3. I suspect that the swagger library that comes
# with flask-restx only understands version 2. By using the steps above, we trick
# swagger into sending the "Authorization" header. You just have to add the word
# "Bearer" yourself when pasting the token.
#
# https://swagger.io/docs/specification/authentication/bearer-authentication/
# https://swagger.io/docs/specification/2-0/authentication/api-keys/

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    },
    'password': {
        'type': 'basic'
    }
}

bp = Blueprint('api', __name__)
api = Api(bp, authorizations=authorizations, security='apikey')

from odyssey.api.client_services.routes import ns
api.add_namespace(ns)

from odyssey.api.client.routes import ns
api.add_namespace(ns)

from odyssey.api.doctor.routes import ns
api.add_namespace(ns)

from odyssey.api.facility.routes import ns
api.add_namespace(ns)

from odyssey.api.lookup.routes import ns
api.add_namespace(ns)

from odyssey.api.maintenance.routes import ns
api.add_namespace(ns)

from odyssey.api.notifications.routes import ns
api.add_namespace(ns)

from odyssey.api.payment.routes import ns
api.add_namespace(ns)

from odyssey.api.physiotherapy.routes import ns
api.add_namespace(ns)

from odyssey.api.practitioner.routes import ns
api.add_namespace(ns)

from odyssey.api.staff.routes import ns
api.add_namespace(ns)

from odyssey.api.system.routes import ns
api.add_namespace(ns)

from odyssey.api.telehealth.routes import ns
api.add_namespace(ns)

from odyssey.api.trainer.routes import ns
api.add_namespace(ns)

from odyssey.api.user.routes import ns
api.add_namespace(ns)

from odyssey.api.version.routes import ns
api.add_namespace(ns)

from odyssey.api.wearables.routes import ns
api.add_namespace(ns)

from odyssey.api.community_manager.routes import ns
api.add_namespace(ns)

from odyssey.api.provider.routes import ns
api.add_namespace(ns)