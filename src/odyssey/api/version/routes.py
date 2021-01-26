from flask import current_app
from flask_accepts import responds
from flask_restx import Resource

from odyssey import db
from odyssey.api import api
from odyssey.utils.auth import token_auth

ns = api.namespace('version', description='Endpoint for API version.')

@ns.route('/')
class VersionEndpoint(Resource):
    @ns.doc(security=None)
    @responds({'name': 'version', 'type': str},{'name': 'db_version', 'type': str}, status_code=200, api=ns)
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
        db_version = db.session.execute("Select * from alembic_version;").fetchall()
        
        return {'version': current_app.config['VERSION'], 'db_version': db_version[0][0]}
