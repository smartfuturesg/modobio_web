""" 
Flask app configuration
=======================

Defaults
--------

The API is configured by settings in :mod:`odyssey.defaults`. Each parameter in defaults can
be overridden by setting an environmental variable with the same name (all upper case).

Debug
-----

``FLASK_DEBUG`` is the environmental variable that sets Flask debugging mode to provide
code reloading and better error messages. Options are ``true, 1, yes`` or ``false, 0, no``.

Debug mode is set by Flask very early on in the process, before the configuration is loaded.
It can therefore not be set in this configuration. From https://flask.palletsprojects.com/en/2.2.x/config/#DEBUG: "config['DEBUG'] may not
behave as expected if set in code."

What we can do, is check afterwards if it was set or not. We demand that it is set, either
on or off and raise an error if it is not set. This forces the user to make a concious
decision when running the API.

``TESTING`` is picked up by Flask automatically. Do not set it in the environment, it is
set in conftest.py when running pytest.

How to use
----------

In the rest of the API code, any of the variables set in :mod:`odyssey.defaults` can be
called from the config dict::

    from flask import current_app
    val = current_app.config['PARAMETER_NAME']

The API should **always assume to be in production**. Only if there are specific requirements
to introduce dev-only or test-only code, for example a debug endpoint or testing helpers, can
conditionals be used::

    if current_app.debug:
        # True when in development, including testing
        ...
    if current_app.testing:
        # True when running pytest
        ...

In which environments are ``debug`` and ``testing`` enabled?

=======  =====  ======  ====  =======  ====
         local  pytest  dev   staging  prod
=======  =====  ======  ====  =======  ====
debug    T      T       T     ?        F
testing  F      T       F     F        F
=======  =====  ======  ====  =======  ====

AWS and other 3rd party services
--------------------------------

In order for remote development to work, the program must have access to AWS. A client key
ID and secret key must be provided either in ``$HOME/.aws/credentials`` or in the environment as
``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY``, respectively. Additionally, a default
region must be set in ``$HOME/.aws/config`` or ``AWS_DEFAULT_REGION``.

Notes
-----

- This file is loaded by the main Flask app using ``app.config.from_object(Config())``.
- Only uppercase parameters will be added to app.config.

.. deprecated:: release 0.7
   ``FLASK_DEV`` is no longer used.

.. deprecated:: release 1.2.2
    ``FLASK_ENV`` is deprecated by Flask v2.2. Instead, use the ``FLASK_DEBUG`` key
    to enable/disable debugging.
"""

import argparse
import getpass
import os
import secrets
import sys
import textwrap

from typing import Any

import odyssey.defaults

try:
    from odyssey.api.misc import version
except:
    version = None


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
        # Debug has already been enabled by Flask at startup, but we don't
        # have access to current_app here. We still need to know what
        # FLASK_DEBUG was set to, so we can make decisions in the rest of
        # the config and propagate it to scripts outside of Flask.
        # https://flask.palletsprojects.com/en/2.2.x/config/#debug-mode

        # Force debug to be set.
        flask_debug_env = os.getenv('FLASK_DEBUG')
        if flask_debug_env is None:
            # Allow for CLI option --debug/--no-debug
            if '--debug' in sys.argv:
                flask_debug_env = '1'
            elif '--no-debug' in sys.argv:
                flask_debug_env = '0'
            else:
                raise ValueError('FLASK_DEBUG must be set.')

        # Here we propagate the env FLASK_DEBUG setting for external scripts.
        # We don't want to set DEBUG, since that is set by Flask at startup.
        # However, API code should use app.debug and app.testing.
        self.FLASK_DEBUG = True
        if flask_debug_env.lower() in ('false', '0', 'no'):
            self.FLASK_DEBUG = False

        # Are we running flask db ...?
        migrate = (len(sys.argv) > 1 and sys.argv[1] == 'db')

        # Load defaults.
        for varname in odyssey.defaults.__dict__.keys():
            if varname.startswith('__') or not varname.isupper():
                continue

            # Celery expects configuration variables to be lower case and without 
            # the celery_ prefix. That means that they will not be picked up by flask.
            # That is fine, because they are not relevant to Flask. If there is ever a
            # need to access these variables from Flask, simply remove 'continue' and
            # use the upper case, celery_ prefixed version of the variables in Flask.
            if varname.startswith('CELERY_'):
                _, stripped = varname.split('_', maxsplit=1)
                setattr(self, stripped.lower(), self.getvar(varname))
                continue

            setattr(self, varname, self.getvar(varname))

        # No swagger in production.
        self.SWAGGER_DOC = self.FLASK_DEBUG

        # Version info, override from file if exists, but environment takes precedence.
        if version and self.API_VERSION == odyssey.defaults.API_VERSION:
            self.API_VERSION = version

        # Logging
        if not self.LOG_LEVEL:
            self.LOG_LEVEL = 'INFO'
            if self.FLASK_DEBUG:
                self.LOG_LEVEL = 'DEBUG'

        # Database URI.
        if not self.DB_URI:
            name = self.DB_NAME
            if self.TESTING:
                name = self.DB_NAME_TESTING

            self.DB_URI = f'{self.DB_FLAV}://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}/{name}'        

        self.SQLALCHEMY_DATABASE_URI = self.DB_URI

        # S3 prefix
        if self.FLASK_DEBUG and self.AWS_S3_PREFIX == odyssey.defaults.AWS_S3_PREFIX:
            if self.TESTING:
                rand = secrets.token_hex(3)
                self.AWS_S3_PREFIX = f'temp/pytest-{rand}'
            else:
                username = getpass.getuser()
                self.AWS_S3_PREFIX = f'{username}'

        # Telehealth timing
        if self.FLASK_DEBUG:
            self.TELEHEALTH_BOOKING_LEAD_TIME_HRS = 0
            self.TELEHEALTH_BOOKING_TRANSCRIPT_EXPIRATION_HRS = 0.5

    def getvar(self, var: str) -> Any:
        """ Get a configuration setting.

        Order of lookup:

        1. Environmental variables,
        2. Defaults from :mod:`odyssey.defaults`,
        3. None if all else fails.

        Parameters
        ----------
        var : str
            Name of the configuration variable, which has the same name as the
            environmental variable and the variable in :mod:`odyssey.defaults`.

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

        return getattr(odyssey.defaults, var, None)

def database_parser() -> argparse.ArgumentParser:
    """ Return CLI parser for database arguments.

    For use in scripts that need to access the database, but are not under control
    of Flask. Use this function for full control over and extension of command line
    parameters. For the database URI as a string without further control, use
    :func:`database_uri`.

    Returns
    -------
    argparse.ArgumentParser
        Command line argument parser, useful for extending functionality.
    """

    help_text = """
    Pass the URI of the database with the command line argument `--db_uri` or as an
    environmental variable ``DB_URI``.

    The database URI can also be constructed from the following partial parameters:

    - DB_FLAV: the database "flavour" or dialect.
    - DB_USER: the database username.
    - DB_PASS: the password for the user.
    - DB_HOST: the hostname or IP address of the database server.
    - DB_NAME: the name of the database.

    The commandline argument takes precedence over ``DB_URI``, which in turn takes
    precedence over the partial parameters. Defaults are taken from :mod:`odyssey.defaults`
    """
    conf = Config()

    parser = argparse.ArgumentParser(
        description=textwrap.dedent(help_text),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--db_uri',
        default=conf.DB_URI,
        help='Database URI postgres://<user>:<pass>@<host>/<db>')

    return parser

def database_uri() -> str:
    """ Database URI as a string.

    For use in scripts that need to access the database, but are not under control
    of Flask. For more control over the options and an extendible command line
    parser, use :func:`database_parser`.

    Returns
    -------
    str
        URI of the database.
    """
    parser = database_parser()
    args = parser.parse_args()

    return args.db_uri
