from flask import current_app
from flask_accepts import responds
from flask_restx import Resource

from odyssey.api import api
from odyssey.utils.auth.odyssey_auth import token_auth

ns = api.namespace('version', description='Endpoint for API version.')

@ns.route('/')
class VersionEndpoint(Resource):
    @token_auth.login_required
    @responds({'name': 'version', 'type': str}, status_code=200, api=ns)
    def get(self):
        """ Returns API version in response to a GET request.

        Version number can come from :mod:`odyssey.version`, generated by
        setuptools_scm, or from environmental variable ``API_VERSION``.
        The environmental variable takes precedence.

        Returns
        -------
        str
            API version number
        """
        return {'version': current_app.config['VERSION']}
