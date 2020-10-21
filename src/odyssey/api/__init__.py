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

from odyssey.api import (
    clients,
    doctor,
    errors,
    pt,
    remote_clients,
    staff,
    tokens,
    trainer,
    wearables,
    version,
    registered_facilities,
    users
)
