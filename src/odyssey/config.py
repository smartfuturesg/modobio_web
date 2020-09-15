""" Flask app configuration

The configuration of this program is defined by two environmental parameters, ``FLASK_ENV``
and ``FLASK_DEV``. ``FLASK_ENV`` is native to Flask and can be either ``production`` (the
default), or ``development``. Setting ``FLASK_ENV`` to ``development`` enables debugging
and automatic reloading of changed code.

``FLASK_DEV`` determines the development environment and can be either ``local`` or
``remote``. In local development, all storage (database and files) are kept on the localhost.
Configuration parameters are read from :mod:`odyssey.defaults`.

When ``FLASK_DEV`` is set to ``remote``, the default configuration parameters are obtained
from the AWS Parameter store where possible. The database is a database on a separate machine,
and files are stored in AWS S3 buckets.

.. rubric:: Defaults

Configuration parameters can be set in one of four ways (in order of precedense):

1. AWS Parameter Store, if available
2. Environmental variables
3. Defaults from :mod:`odyssey.defaults`
4. Hard-coded defaults is all else fails

Defaults are set in :mod:`odyssey.defaults`. These defaults can be overriden by setting an
environmental variable with the same name. If AWS credentials are available and FLASK_ENV
= "remote", most (but not all) parameters are pulled from the AWS parameter store.

.. rubric:: AWS access

In order for remote development to work, the program must have access to AWS. A client key
ID and secret key must be provided either in ``.aws/credentials`` or in the environment as
``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY``, respectively. Additinally, a default
region must be set (currently "us-east-2") in ``.aws/config`` or ``AWS_DEFAULT_REGION``.

.. rubric:: Special cases

- *Testing*: when ``pytest`` is running the unit tests, the environment is always local (FLASK_DEV =
"local", LOCAL_CONFIG = True).
- *Production*: when ``FLASK_ENV`` is ``development``, the environment is always remote (FLASK_DEV = "remote", LOCAL_CONFIG = False).

Notes
-----

- This file is loaded by the main Flask app using ``app.config.from_object(Config())``.
- Only uppercase attributes defined on the Config instance will be added to app.config.
- The development environment is accessible in the Flask program as ``LOCAL_CONFIG`` (bool).
"""

import boto3
import os
import pathlib
import sys

from botocore.exceptions import NoCredentialsError

from odyssey import defaults

try:
    from odyssey.version import version as version_file
except:
    version_file = None


class Config:
    """ Main configuration class.

    This class needs to be instantiated before it can be loaded by Flask.
    Load this class from the :func:`odyssey.create_app` app factory:

    .. code-block::

        def create_app():
            app = Flask(__name__)
            app.config.from_object(Config())
    """

    def __init__(self):
        # Are we running pytest?
        testing = 'pytest' in sys.modules

        # Are we running flask db ...?
        migrate = (len(sys.argv) > 1 and sys.argv[1] == 'db')

        # Do we want to keep everything local?
        flask_dev = os.getenv('FLASK_DEV', default=defaults.FLASK_DEV)
        if flask_dev not in ('local', 'remote'):
            raise ValueError(f'FLASK_DEV must be "local" or "remote", found "{flask_dev}".')

        flask_env = os.getenv('FLASK_ENV', default='production')
        if flask_env not in ('development', 'production'):
            raise ValueError(f'FLASK_ENV must be "development" or "production", found "{flask_env}".')

        self.LOCAL_CONFIG = flask_dev == 'local'

        if testing:
            self.LOCAL_CONFIG = True

        if flask_env == 'production':
            self.LOCAL_CONFIG = False

        # Do we have access to AWS Parameter store?
        self.ssm = None
        if not self.LOCAL_CONFIG:
            try:
                self.ssm = boto3.client('ssm')
                self.ssm.describe_parameters()
            except NoCredentialsError:
                self.ssm = None
                self.LOCAL_CONFIG = True

        #############################################################
        
        # Database
        db_flav = self.getvar('DB_FLAV', '/modobio/odyssey/db_flav')
        db_host = self.getvar('DB_HOST', '/modobio/odyssey/db_host')

        if testing:
            db_name = 'modobio_test'
        else:
            db_name = self.getvar('DB_NAME', '/modobio/odyssey/db_name')

        if migrate:
            db_user = self.getvar('DB_USER', '/modobio/odyssey/db_user_master')
            db_pass = self.getvar('DB_PASS', '/modobio/odyssey/db_pass_master', decrypt=True)
        else:
            db_user = self.getvar('DB_USER', '/modobio/odyssey/db_user')
            db_pass = self.getvar('DB_PASS', '/modobio/odyssey/db_pass', decrypt=True)

        self.SQLALCHEMY_DATABASE_URI = f'{db_flav}://{db_user}:{db_pass}@{db_host}/{db_name}'

        # S3 buckets
        if flask_env == 'production':
            self.DOCS_BUCKET_NAME = self.getvar('DOCS_BUCKET_NAME', '/modobio/odyssey/docs_bucket')
        else:
            self.DOCS_BUCKET_NAME = self.getvar('DOCS_BUCKET_NAME', '/modobio/odyssey/docs_bucket_test')

        # Wearables
        self.OURA_CLIENT_ID = self.getvar(
            'OURA_CLIENT_ID',
            '/modobio/wearables/plugins/oura/client_id'
        )
        self.OURA_CLIENT_SECRET = self.getvar(
            'OURA_CLIENT_SECRET',
            '/modobio/wearables/plugins/oura/client_secret',
            decrypt=True
        )
        self.OURA_AUTH_URL = self.getvar('OURA_AUTH_URL', None)
        self.OURA_TOKEN_URL = self.getvar('OURA_TOKEN_URL', None)

        # Other config
        self.SECRET_KEY = self.getvar('SECRET_KEY', '/modobio/odyssey/app_secret')
        self.SQLALCHEMY_TRACK_MODIFICATIONS = self.getvar('SQLALCHEMY_TRACK_MODIFICATIONS', None)

        # Testing config
        if testing:
            self.TESTING = True
            self.WTF_CSRF_ENABLED = False
        else:
            self.TESTING = self.getvar('TESTING', None, default=False)
            self.WTF_CSRF_ENABLED = self.getvar('WTF_CSRF_ENABLED', None, default=True)

        # Version info
        version_env = os.getenv('API_VERSION')
        if version_env:
            self.VERSION = version_env
        elif version_file:
            self.VERSION = version_file
        else:
            self.VERSION = 'unknown version'

    def getvar(self, var, param, decrypt=False, default=''):
        """ Get a configuration setting.

        Order of lookup:

        1. AWS Parameter Store
        2. Environmental variables
        3. Defaults from :mod:`odyssey.defaults`
        4. Given ``default`` (defaults to '') if all else fails

        Parameters
        ----------
        var : str
            Name of the configuration variable, which has the same name as the
            environmental variable and the variable in :mod:`odyssey.defaults`.

        param : str
            Name of the parameter on the AWS Parameter Store. AWS lookup will
            be skipped if param is None.

        Returns
        -------
        str
            Value of the parameter.
        """
        if not self.LOCAL_CONFIG and param:
            return self.ssm.get_parameter(Name=param, WithDecryption=decrypt)['Parameter']['Value']

        return os.getenv(var, default=getattr(defaults, var, default))
