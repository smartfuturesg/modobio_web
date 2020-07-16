"""
Flask app configuration
=======================

Flask makes use of environmental variables to changes its behaviour. Since we have multiple
development/testing/production environments, an extra variable is introduced to fine-tune
the behaviour of the app.


FLASK_ENV
---------

``FLASK_ENV`` is a Flask-native variable and has special meaning to Flask. Only two values are
recognized: ``production`` and ``development``. If ``FLASK_ENV`` is not set, it defaults to
``production``. You set ``FLASK_ENV`` in the environment, but it is stored in ``app.config``
as ``ENV``.

Do not repurpose this variable. Flask may add new functionality in the future that is dependent
on this variable. Keep this variable as it is and respect its values.


FLASK_DEV and :attr:`flask_dev`
-------------------------------

This is a new variable to indicate which development environment is being used. At the moment,
there are 5 possible options: ``local`` for local development, ``development`` for development
on the AWS development server, ``test`` for running unit tests, ``production`` for the live
production environment, and ``mock`` which is identical to production, except that a database
with mock data is used.

The main difference between ``local`` and ``test`` and the other settings is that development
on the local computer does not use any AWS parameters or S3 storage. Everything is kept locally.
For the other settings development, mock data, and production, all takes place on AWS servers
and therefore options such as AWS parameter store and S3 storage are available.

In stead of setting environmental variable `FLASK_DEV`, it is also possible to pass the
parameter :attr:`flask_dev` to app factory :func:`odyssey.create_app`. It has the same meaning
and same possible values as `FLASK_DEV`. If both are set, :attr:`flask_dev` takes precedence
over `FLASK_DEV`.


FLASK_DEV = local
-----------------

This is the default if ``FLASK_ENV`` is ``development``. Its intended use is local developement.
The database used is also on localhost. The following environmental variables can be used to
further fine-tune the database connection.

``FLASK_DB_FLAV``: database type, default: postgres
``FLASK_DB_USER``: database username, default: empty
``FLASK_DB_PASS``: database password, default: empty
``FLASK_DB_HOST``: database hostname, default: localhost
``FLASK_DB_NAME``: database name, default: modobio

The above variables default to the following connection string: postgres://localhost/modobio


FLASK_DEV = development
-----------------------

This setting is to be used on the development servers. It uses the AWS parameter store to
discover database and other settings.


FLASK_DEV = test
----------------

This setting is to be used on local machines for unit testing with pytest. It sets ``TESTING=True``
and enables a few testing specific settings. For database settings, see ``FLASK_DEV = local``, above.

The default database string: sqlite://<path_to_odyssey_installation>/app.db


FLASK_DEV = mock
----------------

This setting is to be used on production server, but serving mock data. It uses the AWS
parameter store to discover database and other settings.


FLASK_DEV = production
----------------------

This is the default if ``FLASK_ENV`` is ``production`` or unset. It is to be used on the
live production server. It uses the AWS parameter store to discover database and other settings.


Notes
-----

This file is loaded by the main Flask app using ``app.config.from_object(Config())``.
Only uppercase attributes in the Config class will be added to app.config.
"""

import boto3
import os
import pathlib
import tempfile

# Possible values
flask_env_options = ('development', 'production')
flask_dev_options = ('local', 'development', 'test', 'mock', 'production')


class Config():
    """ Main configuration class.

    This class needs to be instantiated before it can be loaded by Flask.
    Load this class from the :func:`odyssey.create_app` app factory:

        def create_app(flask_dev=None):
            app = Flask(__name)
            app.config.from_object(Config(flask_dev=flask_dev))

    Then create an app instance by either setting the environmental variables,
    or passing in the parameter. On the command line

    .. code-block:: shell
        export FLASK_ENV=development
        export FLASK_APP=odyssey:create_app("local")
        flask run

    is equivalent to

    .. code-block:: shell
        export FLASK_ENV=development
        export FLASK_DEV=local
        export FLASK_APP=odyssey:create_app
        flask run
    """

    # Defaults
    DOCS_BUCKET_NAME = tempfile.TemporaryDirectory().name
    DOCS_STORE_LOCAL = True
    SECRET_KEY = 'dev'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    def __init__(self, flask_dev=None):
        """ Instantiate the Config class.

        Parameters
        ----------
        flask_dev : str
            Set the configuration options for this specific development environment.
            See module documentation for further explanation.

        Raises
        ------
        ValueError
            Raised when `FLASK_ENV`, `FLASK_DEV`, or :attr:`flask_dev` are set to
            unsupported values.
        """
        # Parameter has precedence over environmental variable
        flask_dev = flask_dev if flask_dev else os.getenv('FLASK_DEV')

        # Flask default is production
        flask_env = os.getenv('FLASK_ENV', 'production')

        # Check that options are valid
        if flask_env and flask_env not in flask_env_options:
            raise ValueError(f'FLASK_ENV must be one of {flask_env_options} or unset. '
                             f'Detected FLASK_ENV={flask_env} which is not supported.')

        if flask_dev and flask_dev not in flask_dev_options:
            raise ValueError(f'FLASK_DEV must be one of {flask_dev_options} or unset. '
                             f'Detected FLASK_DEV={flask_dev} which is not supported.')

        # Set default based on flask_env
        if not flask_dev:
            if flask_env == 'development':
                flask_dev = 'local'
            else:
                flask_dev = 'production'

        # Load the config parameters
        if flask_dev == 'local':
            self.local_config()
        elif flask_dev == 'development':
            self.development_config()
        elif flask_dev == 'test':
            self.test_config()
        elif flask_dev == 'mock':
            self.mock_config()
        else:
            self.production_config()

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        if self.db_user:
            if self.db_pass:
                uri = f'{self.db_flav}://{self.db_user}:{self.db_pass}@{self.db_host}/{self.db_name}'
            else:
                uri = f'{self.db_flav}://{self.db_user}@{self.db_host}/{self.db_name}'
        else:
            uri = f'{self.db_flav}://{self.db_host}/{self.db_name}'
        return uri

    def local_config(self):
        """ Config for local development. """
        self.db_flav = os.getenv('FLASK_DB_FLAV', default='postgres')
        self.db_user = os.getenv('FLASK_DB_USER', default=None)
        self.db_pass = os.getenv('FLASK_DB_PASS', default=None)
        self.db_host = os.getenv('FLASK_DB_HOST', default='localhost')
        self.db_name = os.getenv('FLASK_DB_NAME', default='modobio')

    def development_config(self):
        """ Config for the development server. """
        self.ssm = boto3.client('ssm')
        self.db_flav = self.ssm.get_parameter(Name='/modobio/odyssey/db_flav')['Parameter']['Value']
        self.db_user = self.ssm.get_parameter(Name='/modobio/odyssey/db_user')['Parameter']['Value']
        self.db_pass = self.ssm.get_parameter(Name='/modobio/odyssey/db_pass',
                                              WithDecryption=True)['Parameter']['Value']
        self.db_host = self.ssm.get_parameter(Name='/modobio/odyssey/db_host')['Parameter']['Value']
        self.db_name = self.ssm.get_parameter(Name='/modobio/odyssey/db_name_dev')['Parameter']['Value']

        param = self.ssm.get_parameter(Name='/modobio/odyssey/docs_bucket_test')
        self.DOCS_BUCKET_NAME = param['Parameter']['Value']
        self.DOCS_STORE_LOCAL = False

    def test_config(self):
        """ Config for running unit tests. """
        db_file = pathlib.Path(__file__).absolute().parent / 'app.db'
        self.db_flav = os.getenv('FLASK_DB_FLAV', default='sqlite')
        self.db_user = os.getenv('FLASK_DB_USER', default=None)
        self.db_pass = os.getenv('FLASK_DB_PASS', default=None)
        self.db_host = os.getenv('FLASK_DB_HOST', default='')
        self.db_name = os.getenv('FLASK_DB_NAME', default=db_file)

        self.DOCS_BUCKET_NAME = tempfile.TemporaryDirectory().name
        self.DOCS_STORE_LOCAL = True

        # These are specific to test environment
        self.TESTING = True
        self.WTF_CSRF_ENABLED = False
        self.BCRYPT_LOG_ROUNDS = 4

    def production_config(self):
        """ Config for production environment. """
        self.ssm = boto3.client('ssm')
        self.db_flav = self.ssm.get_parameter(Name='/modobio/odyssey/db_flav')['Parameter']['Value']
        self.db_user = self.ssm.get_parameter(Name='/modobio/odyssey/db_user')['Parameter']['Value']
        self.db_pass = self.ssm.get_parameter(Name='/modobio/odyssey/db_pass',
                                              WithDecryption=True)['Parameter']['Value']
        self.db_host = self.ssm.get_parameter(Name='/modobio/odyssey/db_host')['Parameter']['Value']
        self.db_name = self.ssm.get_parameter(Name='/modobio/odyssey/db_name')['Parameter']['Value']

        param = self.ssm.get_parameter(Name='/modobio/odyssey/docs_bucket')
        self.DOCS_BUCKET_NAME = param['Parameter']['Value']
        self.DOCS_STORE_LOCAL = False
        self.SECRET_KEY = self.ssm.get_parameter(Name='/modobio/odyssey/app_secret',
                                                 WithDecryption=True)['Parameter']['Value']

    def mock_config(self):
        """ Config like production environment but with mock data. """
        self.production_config()
        self.db_name = self.ssm.get_parameter(Name='/modobio/odyssey/db_name_test')['Parameter']['Value']
