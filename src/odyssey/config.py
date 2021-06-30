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
        # Are we running pytest?
        testing = 'pytest' in sys.modules

        # Are we running flask db ...?
        migrate = (len(sys.argv) > 1 and sys.argv[1] == 'db')

        # Are we running in development mode?
        flask_env = os.getenv('FLASK_ENV')

        # Testing (running pytest) is always dev.
        if testing:
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
        self.SWAGGER_DOC = self.DEV

        # Testing is always true when running pytest.
        self.TESTING = testing

        # Version info, override from file if exists, but environment takes precedence.
        if version and self.API_VERSION == odyssey.defaults.API_VERSION:
            self.API_VERSION = version

        # Database URI.
        if not self.DB_URI:
            name = self.DB_NAME
            if testing:
                name = self.DB_NAME_TESTING

            self.DB_URI = f'{self.DB_FLAV}://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}/{name}'        

        self.SQLALCHEMY_DATABASE_URI = self.DB_URI

        # S3 prefix
        if self.DEV and self.AWS_S3_PREFIX == odyssey.defaults.AWS_S3_PREFIX:
            if testing:
                rand = secrets.token_hex(3)
                self.AWS_S3_PREFIX = f'pytest-{rand}'
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

        return getattr(odyssey.defaults, var, None)


def database_uri(docstring: str='') -> str:
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
    database_uri.__doc__ += help_text

    parser = argparse.ArgumentParser(
        description=docstring + textwrap.dedent(help_text),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--db_uri', help="Database URI postgres://<user>:<pass>@<host>/<db>")
    args = parser.parse_args()

    conf = Config()
    db_uri = args.db_uri or conf.DB_URI

    return db_uri
