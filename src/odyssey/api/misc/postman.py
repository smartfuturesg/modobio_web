import logging
logger = logging.getLogger(__name__)

from flask import current_app, json, Response
from flask_restx import Namespace

from odyssey.utils.base.resources import BaseResource

# Development-only namespace
ns_dev = Namespace('postman', description='[DEV ONLY] Endpoint to download a Postman collection of the API.')

@ns_dev.route('/')
class PostmanEndpoint(BaseResource):
    @ns_dev.doc(security=None)
    def get(self):
        """ Download API as a Postman collection.

        This endpoint provides a convenient way to download the entire API as a Postman collection.
        It returns a JSON file for download. That JSON file can be imported into Postman and provides
        a collection containing all endpoints in this API.
        """
        data = json.dumps(ns_dev.apis[0].as_postman(urlvars=True, swagger=True), indent=2)

        response = Response(
            data,
            mimetype='application/json',
            direct_passthrough=True)

        version = current_app.config['API_VERSION']
        filename = f'ModoBio API v{version}.json'
        response.headers.set('Content-Disposition', 'attachment', filename=filename)
        return response
