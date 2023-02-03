""" 
Flask app configuration
=======================

The configuration of the Odyssey API follows the Flask environmental variable ``FLASK_ENV``,
but with stricter requirements. Here, it is only allowed to be set to ``production`` or 
``development``. Any other value for ``FLASK_ENV`` will raise an error. Not setting
``FLASK_ENV`` in the environment will also raise an error, forcing the user to make a
concious decision when running the API. There is no default value for ``FLASK_ENV``.

Defaults
========

The API is configured by settings in :mod:`odyssey.defaults`. Each parameter in defaults can
be overridden by setting an environmental variable with the same name (all upper case).

How to use
==========

In the rest of the API code, any of the variables set in :mod:`odyssey.defaults` can be
called from the config dict::

    from flask import current_app
    val = current_app.config['PARAMETER_NAME']

The API should **always assume to be in production**. Only if there are specific requirements
to introduce dev-only or test-only code, for example a debug endpoint or testing helpers, can
conditionals be used::

    if current_app.config['DEV']:
        # True when in development
        ...
    if current_app.config['TESTING']:
        # True when running pytest
        ...

AWS and other 3rd party services
================================

In order for remote development to work, the program must have access to AWS. A client key
ID and secret key must be provided either in ``$HOME/.aws/credentials`` or in the environment as
``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY``, respectively. Additionally, a default
region must be set in ``$HOME/.aws/config`` or ``AWS_DEFAULT_REGION``.

Notes
=====

- This file is loaded by the main Flask app using ``app.config.from_object(Config())``.
- Only uppercase parameters will be added to app.config.

.. deprecated:: release 0.7
   ``FLASK_DEV`` is no longer used.
"""

import argparse
import getpass
import os
import secrets
import sys
import textwrap

from typing import Any

import packaging

import odyssey.defaults


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
        self.TESTING = 'pytest' in sys.modules

        # Are we running flask db ...?
        migrate = (len(sys.argv) > 1 and sys.argv[1] == 'db')

        # Are we running in development mode?
        flask_env = os.getenv('FLASK_ENV')

        # Testing (running pytest) is always dev.
        if self.TESTING:
            flask_env = 'development'

        # FLASK_ENV is loaded by Flask before the app is created and thus
        # before this config is loaded. The default is "production" if
        # FLASK_ENV was not set. We don't want production by default, so raise
        # an error if it was not set to force the user to set it explicitly.
        if flask_env not in ('development', 'production'):
            raise ValueError(f'FLASK_ENV must be either "development" or "production", '
                             f'found "{flask_env}".')

        # Simple boolean switch for main code.
        self.DEV = flask_env == 'development'

        # Load defaults.
        for var in odyssey.defaults.__dict__.keys():
            if var.startswith('__') or not var.isupper():
                continue

            # Celery expects configuration variables to be lower case and without 
            # the celery_ prefix. That means that they will not be picked up by flask.
            # That is fine, because they are not relevant to Flask. If there is ever a
            # need to access these variables from Flask, simply remove 'continue' and
            # use the upper case, celery_ prefixed version of the variables in Flask.
            if var.startswith('CELERY_'):
                _, stripped = var.split('_', maxsplit=1)
                setattr(self, stripped.lower(), self.getvar(var))
                continue

            setattr(self, var, self.getvar(var))

        # Find version
        self.get_version()

        # No swagger in production.
        self.SWAGGER_DOC = self.DEV

        # Logging
        if not self.LOG_LEVEL:
            self.LOG_LEVEL = 'INFO'
            if self.DEV:
                self.LOG_LEVEL = 'DEBUG'

        # Database URI.
        if not self.DB_URI:
            name = self.DB_NAME
            if self.TESTING:
                name = self.DB_NAME_TESTING

            self.DB_URI = f'{self.DB_FLAV}://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}/{name}'        

        self.SQLALCHEMY_DATABASE_URI = self.DB_URI

        # S3 prefix
        if self.DEV and self.AWS_S3_PREFIX == odyssey.defaults.AWS_S3_PREFIX:
            if self.TESTING:
                rand = secrets.token_hex(3)
                self.AWS_S3_PREFIX = f'temp/pytest-{rand}'
            else:
                username = getpass.getuser()
                self.AWS_S3_PREFIX = f'{username}'

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

        # Not in environment, get from defaults or return None.
        return getattr(odyssey.defaults, var, None)

    def dump(self) -> str:
        """ Pretty print all config variables into a string.

        Returns
        -------
        str
            All configuration variables and their values in a single string.
        """
        conf = ['Configuration:']
        for var, val in sorted(self.__dict__.items()):
            if var.startswith('__') or not var.isupper():
                continue
            conf.append(f'   {var} = {val}')
        return '\n'.join(conf)

    def get_version(self):
        """ Get and parse version string.

        This function will try to obtain a version string from the following sources:

        1. environment variable ``API_VERSION``,
        2. the git branch name if it starts with "release-".

        The version will then be parsed and saved under the following variables:

        - VERSION, :class:`packaging.version.Version` instance,
        - VERSION_STRING, full version string with "release-" prefix,
        - VERSION_BRANCH, same as version string but with "major.minor" digits only.

        If a parsable version string cannot be found, VERSION will be Version(0)
        and VERSION_BRANCH and VERSION_STRING will be set to whatever was found,
        unparsed.

        What that means in practice is that on a feature branch (e.g. NRV-XXXX-abc)
        that name will be used (and Version(0)) and on release branches the version
        number will be used ("release-1.2.3" and Version(1.2.3)).
        """
        version = self.getvar('API_VERSION')

        if not version:
            head = ''
            here = pathlib.Path(__file__)
            for p in here.parents:
                if (p / '.git' / 'HEAD').exists():
                    head = (p / '.git' / 'HEAD').read_text()
                    break
            version = head.strip().split('/')[-1]

        if version and version.startswith('release-'):
            version = version[7:]

        try:
            self.VERSION = packaging.version.parse(version)
        except packaging.version.InvalidVersion:
            self.VERSION = packaging.version.parse('0')
            self.VERSION_BRANCH = version
            self.VERSION_STRING = version
        else:
            # packaging.version does not store 4th digit.
            if len(self.VERSION.release) > 3:
                self.VERSION.build = self.VERSION.release[3]

            self.VERSION_BRANCH = f'release-{self.VERSION.major}.{self.VERSION.minor}'
            self.VERSION_STRING = self.VERSION_BRANCH + f'.{self.VERSION.micro}.{self.VERSION.build}'


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
