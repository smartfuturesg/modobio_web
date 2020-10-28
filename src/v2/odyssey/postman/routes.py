""" Download API as a Postman collection.

This endpoint is not part of the flask-restx based API, instead it is implemented
as a plain Flask route. It is only available in developer mode, when run 
with ``FLASK_DEV=local``.

When accessing this endpoint at http://localhost/api/postman, it returns a
JSON file for download. That JSON file can be imported into Postman and provides
a collection containing all endpoints in this API.
"""

from flask import json, Response
from flask import Blueprint
from odyssey.api import api

bp = Blueprint('postman', __name__)

@bp.route('/', methods=('GET',))
def postman():
    data = json.dumps(api.as_postman(urlvars=True, swagger=True), indent=2)

    response = Response(
        data,
        mimetype='application/json',
        direct_passthrough=True,
    )
    response.headers.set('Content-Disposition', 'attachment', filename='postman.json')
    return response
