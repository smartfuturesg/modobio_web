""" 
Flask app configuration
=======================

The configuration of the Odyssey API is defined by two environmental parameters, ``FLASK_ENV``
and ``FLASK_DEV``.

``FLASK_ENV`` is native to Flask and can be set to ``production`` (the
default) or ``development``. Setting ``FLASK_ENV=development`` enables debugging
and automatic reloading of changed code.

``FLASK_DEV`` determines the development environment and can be either ``local`` or
``remote``. In local development, all storage (database and files) are kept on the localhost.
Configuration parameters are read from :mod:`odyssey.defaults`.

When ``FLASK_DEV`` is set to ``remote``, the default configuration parameters are obtained
from the AWS Parameter store where possible. The database is a database on a separate machine,
and files are stored in AWS S3 buckets.

Defaults
========

Configuration parameters can be set in one of four ways (in order of precedense):

1. Environmental variables
2. AWS Parameter Store, if available
3. Defaults from :mod:`odyssey.defaults`
4. Hard-coded defaults if all else fails

Defaults are set in :mod:`odyssey.defaults`. These defaults can be overriden by setting an
environmental variable with the same name. If AWS credentials are available and
``FLASK_ENV=remote``, default parameters are pulled from the AWS parameter store.

AWS access
==========

In order for remote development to work, the program must have access to AWS. A client key
ID and secret key must be provided either in ``$HOME/.aws/credentials`` or in the environment as
``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY``, respectively. Additionally, a default
region must be set in ``$HOME/.aws/config`` or ``AWS_DEFAULT_REGION``.

Special cases
=============

**Testing**: when ``pytest`` is running the unit tests, the environment is always local
(i.e. ``FLASK_DEV=local`` and ``LOCAL_CONFIG=True``).

**Production**: when ``FLASK_ENV=development``, the environment is always remote
(i.e. ``FLASK_DEV=remote`` and  ``LOCAL_CONFIG=False``).

Notes
=====

- This file is loaded by the main Flask app using ``app.config.from_object(Config())``.
- Only uppercase attributes defined on the Config instance will be added to app.config.
- The development environment is accessible in the Flask program as ``LOCAL_CONFIG`` (bool).
- **Do NOT** use any other logic to determine what state the app is in. All configuration
  logic should take place in config.py.
"""

import boto3
import os
import sys

from typing import Any
from botocore.exceptions import NoCredentialsError

from odyssey import defaults

try:
    from odyssey.api.misc import version as version_file
except:
    version_file = None


class Config:
    """ Main configuration class.

    This class needs to be instantiated before it can be loaded by Flask.
    Load this class in the :func:`odyssey.create_app` app factory using
    :meth:`flask.Config.from_object`.

    .. code-block::

        from odyssey.config import Config

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
        flask_env = os.getenv('FLASK_ENV')

        # Testing (running pytest) is always local.
        if testing:
            flask_env = 'development'
            flask_dev = 'local'

        if flask_dev not in ('local', 'remote'):
            raise ValueError(f'FLASK_DEV must be "local" or "remote", found "{flask_dev}".')

        # FLASK_ENV is loaded by Flask before the app is created and thus
        # before this config is loaded. The default is "production" if
        # FLASK_ENV was not set. We don't want production by default, so raise
        # an error if it was not set to force the user to set it explicitly.
        if not flask_env:
            raise ValueError('FLASK_ENV was not set. Set it to '
                             'either "development" or "production".')
        elif flask_env not in ('development', 'production'):
            raise ValueError(f'FLASK_ENV must be "development" or '
                             f'"production", found "{flask_env}".')

        self.LOCAL_CONFIG = flask_dev == 'local'

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
        db_flav = self.getvar('DB_FLAV', None)
        db_host = self.getvar('DB_HOST', None)

        if testing:
            db_name = 'modobio_test'
        else:
            db_name = self.getvar('DB_NAME', None)

        if migrate:
            db_user = self.getvar('DB_USER', '/modobio/odyssey/db_user_master')
            db_pass = self.getvar('DB_PASS', '/modobio/odyssey/db_pass_master', decrypt=True)
        else:
            db_user = self.getvar('DB_USER', '/modobio/odyssey/db_user')
            db_pass = self.getvar('DB_PASS', '/modobio/odyssey/db_pass', decrypt=True)

        self.SQLALCHEMY_DATABASE_URI = f'{db_flav}://{db_user}:{db_pass}@{db_host}/{db_name}'

        # S3 bucket
        if self.LOCAL_CONFIG:
            self.S3_BUCKET_NAME = defaults.S3_BUCKET_NAME
        else:
            # Don't use getvar, must fail if not set in environment
            self.S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

            if not self.S3_BUCKET_NAME:
                raise ValueError('S3_BUCKET_NAME not defined')

        # Whooshee fulltext index
        self.WHOOSHEE_DIR = self.getvar('WHOOSHEE_DIR', None)

        # Wearables
        self.OURA_CLIENT_ID = self.getvar(
            'OURA_CLIENT_ID',
            '/modobio/wearables/oura/client_id'
        )
        self.OURA_CLIENT_SECRET = self.getvar(
            'OURA_CLIENT_SECRET',
            '/modobio/wearables/oura/client_secret',
            decrypt=True
        )
        self.OURA_AUTH_URL = self.getvar('OURA_AUTH_URL', None)
        self.OURA_TOKEN_URL = self.getvar('OURA_TOKEN_URL', None)

        self.FITBIT_CLIENT_ID = self.getvar(
            'FITBIT_CLIENT_ID',
            '/modobio/wearables/fitbit/client_id'
        )
        self.FITBIT_CLIENT_SECRET = self.getvar(
            'FITBIT_CLIENT_SECRET',
            '/modobio/wearables/fitbit/client_secret',
            decrypt=True
        )
        self.FITBIT_AUTH_URL = self.getvar('FITBIT_AUTH_URL', None)
        self.FITBIT_TOKEN_URL = self.getvar('FITBIT_TOKEN_URL', None)

        # Other config
        self.SECRET_KEY = self.getvar('SECRET_KEY', '/modobio/odyssey/app_secret')
        self.SQLALCHEMY_TRACK_MODIFICATIONS = self.getvar('SQLALCHEMY_TRACK_MODIFICATIONS', None, default=False)

        # No swagger in production
        self.SWAGGER_DOC = flask_env != 'production'

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

    def getvar(self, var: str, param: str, decrypt: bool=False, default: Any='') -> Any:
        """ Get a configuration setting.

        Order of lookup:

        1. Environmental variables
        2. AWS Parameter Store
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
        object
            Value of the parameter, interpreted as None, True, False, int, or float if
            possible, str otherwise.
        """
        env = os.getenv(var)

        # getenv always returns a string. Try to interpret
        # a few basic types: None, True/False, int, or float.
        # Otherwise keep as string.
        if env is not None:
            if env.lower() == 'none':
                return None
            elif env.lower() == 'false':
                return False
            elif env.lower() == 'true':
                return True

            try:
                return int(env)
            except ValueError:
                pass

            try:
                return float(env)
            except ValueError:
                pass

            return env

        if not self.LOCAL_CONFIG and param:
            return self.ssm.get_parameter(Name=param, WithDecryption=decrypt)['Parameter']['Value']

        return getattr(defaults, var, default)

import argparse
import textwrap

def database_uri(docstring=''):
    """ Database selection, for use in scripts not under control of Flask.

    Parameters
    ----------
    docstring : str
        Pass in the doctring of the script in which this function is used. The docstring
        will be prepended to the help text of this function. It will show up on the
        command line when the calling script is run without parameters.

    Returns
    -------
    str
        URI of the database.

    Notes
    -----
    """

    help_text = """
    Pass the URI of the database with the command line argument `--db_uri`. If no URI is
    provided, environmental variables will be used to create a URI.

    DB_FLAV: the database "flavour", postgres by default.
    DB_USER: the database username, empty by default.
    DB_PASS: the password for the user, empty by default.
    DB_HOST: the hostname or IP address of the database server, localhost by default.
    DB_NAME: the name of the database, modobio by default.

    Or specify the entire URI in one string as:

    DB_URI: no default, e.g. postgres://user@password:localhost/modobio
    """
    database_uri.__doc__ += help_text

    parser = argparse.ArgumentParser(
        description=docstring + textwrap.dedent(help_text),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--db_uri', help="Database URI postgres://<user>:<pass>@<host>/<db>")
    args = parser.parse_args()

    uri = os.getenv('DB_URI', args.db_uri)

    if not uri:
        db_user = os.getenv('DB_USER', '')
        db_pass = os.getenv('DB_PASS', '')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_flav = os.getenv('DB_FLAV', 'postgresql')
        db_name = os.getenv('DB_NAME', 'modobio')

        uri = f'{db_flav}://{db_user}:{db_pass}@{db_host}/{db_name}'

    return uri
