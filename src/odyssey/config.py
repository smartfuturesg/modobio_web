"""
Flask app configuration
=======================

Flask makes use of environmental variables to changes its behaviour. Since we have multiple
development/testing/production environments, we here introduce an extra variable to fine-tune
the settings.

FLASK_ENV
---------

``FLASK_ENV`` is a Flask-native variable and has special meaning to Flask. Only two values are
recognized: ``production`` and ``development``. If ``FLASK_ENV`` is not set, it defaults to
``production``. You set ``FLASK_ENV`` in the environment, but it is stored in ``app.config``
as ``ENV``.

I do not want to repurpose this variable. Flask may add new functionality in the future.
We will keep it as it is and respect its setting.

FLASK_DEV
---------

This is a new variable to indicate which development environment is being used. At the moment,
there are 4 possible options: ``local`` for local development, ``development`` for development
on the AWS development server, ``production`` for the live production environment, and ``mock``
which is identical to production, except that a database with mock data is used.

The main difference between ``local`` and the other settings is that development on the local
computer does not use any AWS parameters or S3 storage. Everything is kept locally. For the other
settings development, mock data, and production, all takes place on AWS servers and therefore
options such as AWS parameter store and S3 storage are available.


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

This file is loaded by the main Flask app using ``app.config.from_pyfile()``.
Any uppercase variable in this file will be added to app.config

Currently, the config variables set in this file are:
``SECRET_KEY``
``SQLALCHEMY_DATABASE_URI``
``SQLALCHEMY_TRACK_MODIFICATIONS``
"""

import os
import boto3

# Possible values
flask_env_options = ('development', 'production')
flask_dev_options = ('local', 'development', 'mock', 'production')

flask_env = os.getenv('FLASK_ENV')
flask_dev = os.getenv('FLASK_DEV')

# Check that options are valid
if flask_env and flask_env not in flask_env_options:
    raise ValueError(f'FLASK_ENV must be one of {flask_env_options} or unset. '
                     f'Detected FLASK_ENV={flask_env} which is not supported.')

if flask_dev and flask_dev not in flask_dev_options:
    raise ValueError(f'FLASK_DEV must be one of {flask_dev_options} or unset. '
                     f'Detected FLASK_DEV={flask_dev} which is not supported.')

# If FLASK_DEV is not set, its default depends on FLASK_ENV
if not flask_dev:
    if flask_env == 'development':
        flask_dev = 'local'
    else:
        flask_dev = 'production'


if flask_dev == 'local':
    # All development on local host
    db_flav = os.getenv('FLASK_DB_FLAV', default='postgres')
    db_user = os.getenv('FLASK_DB_USER', default=None)
    db_pass = os.getenv('FLASK_DB_PASS', default=None)
    db_host = os.getenv('FLASK_DB_HOST', default='localhost')
    db_name = os.getenv('FLASK_DB_NAME', default='modobio')

    secret = 'dev'

elif flask_dev == 'development':
    # Testing/developing on EC2 development server
    ssm = boto3.client('ssm')
    db_flav = ssm.get_parameter(Name='/modobio/odyssey/db_flav')['Parameter']['Value']
    db_user = ssm.get_parameter(Name='/modobio/odyssey/db_user')['Parameter']['Value']
    db_pass = ssm.get_parameter(Name='/modobio/odyssey/db_pass', WithDecryption=True)['Parameter']['Value']
    db_host = ssm.get_parameter(Name='/modobio/odyssey/db_host')['Parameter']['Value']
    db_name = ssm.get_parameter(Name='/modobio/odyssey/db_name_dev')['Parameter']['Value']

    secret = 'dev'

elif flask_dev == 'mock':
    # Production server, but with mock data
    ssm = boto3.client('ssm')
    db_flav = ssm.get_parameter(Name='/modobio/odyssey/db_flav')['Parameter']['Value']
    db_user = ssm.get_parameter(Name='/modobio/odyssey/db_user')['Parameter']['Value']
    db_pass = ssm.get_parameter(Name='/modobio/odyssey/db_pass', WithDecryption=True)['Parameter']['Value']
    db_host = ssm.get_parameter(Name='/modobio/odyssey/db_host')['Parameter']['Value']
    db_name = ssm.get_parameter(Name='/modobio/odyssey/db_name_test')['Parameter']['Value']

    secret = ssm.get_parameter(Name='/modobio/odyssey/app_secret', WithDecryption=True)['Parameter']['Value']

else:
    # Production settings
    ssm = boto3.client('ssm')
    db_flav = ssm.get_parameter(Name='/modobio/odyssey/db_flav')['Parameter']['Value']
    db_user = ssm.get_parameter(Name='/modobio/odyssey/db_user')['Parameter']['Value']
    db_pass = ssm.get_parameter(Name='/modobio/odyssey/db_pass', WithDecryption=True)['Parameter']['Value']
    db_host = ssm.get_parameter(Name='/modobio/odyssey/db_host')['Parameter']['Value']
    db_name = ssm.get_parameter(Name='/modobio/odyssey/db_name')['Parameter']['Value']

    secret = ssm.get_parameter(Name='/modobio/odyssey/app_secret', WithDecryption=True)['Parameter']['Value']


if db_user:
    if db_pass:
        uri = f'{db_flav}://{db_user}:{db_pass}@{db_host}/{db_name}'
    else:
        uri = f'{db_flav}://{db_user}@{db_host}/{db_name}'
else:
    uri = f'{db_flav}://{db_host}/{db_name}'

SECRET_KEY = secret
SQLALCHEMY_DATABASE_URI = uri
SQLALCHEMY_TRACK_MODIFICATIONS = False
