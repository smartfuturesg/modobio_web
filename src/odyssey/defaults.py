""" Configuration defaults

This file defines the configuration defaults for the entire API. It is loaded by
:mod:`odyssey.config`
"""
# This file is imported by config.py, so should be valid Python
import tempfile

# Do all local development
FLASK_DEV = 'local'
""" Determines the development environment. Can be 'local' or 'remote'. """

# File storage location
# This directory is **NOT** deleted by the program.
# However, using tempfile.TemporaryDirectory() went out of scope
# and was therefore deleted after defaults was loaded, but while
# Flask was still running.
S3_BUCKET_NAME = tempfile.mkdtemp()
"""
Name of the AWS S3 bucket where files are stored. For ``FLASK_DEV=local`` it is
set to a temporary directory.
"""

# Database
DB_FLAV = 'postgresql'
""" Type of database. """

DB_USER = ''
""" Username for database. """

DB_PASS = ''
""" Password for database. """

DB_HOST = 'localhost'
""" Hostname for database. """

DB_NAME = 'modobio'
""" Name of database. """

# Oura Cloud OAuth parameters
OURA_CLIENT_ID = ''
""" Client ID for Oura Ring API. """

OURA_CLIENT_SECRET = ''
""" Client secret for Oura Ring API. """

OURA_AUTH_URL = 'https://cloud.ouraring.com/oauth/authorize'
""" Authorization URL for Oura Ring API. """

OURA_TOKEN_URL = 'https://api.ouraring.com/oauth/token'
""" Token URL for Oura Ring API. """

OURA_SCOPE = 'daily'
""" Oura resources (scopes) to request permission for. """

# Fitbit OAuth parameters
FITBIT_CLIENT_ID = ''
""" Client ID for Fitbit API. """

FITBIT_CLIENT_SECRET = ''
""" Client secret for Fitbit API. """

FITBIT_AUTH_URL = 'https://www.fitbit.com/oauth2/authorize'
""" Authorization URL for Fitbit API. """

FITBIT_TOKEN_URL = 'https://api.fitbit.com/oauth2/token'
""" Token URL for Fitbit API. """

FITBIT_SCOPE = 'activity heartrate nutrition profile sleep weight'
""" Fitbit resources (scopes) to request permission for. """

SECRET_KEY = 'abcdefghijklmnopqrstuvwxyz0123456789'
"""
Flask secret key, used to encrypt sessions amongst other things.
See https://stackoverflow.com/questions/22463939/demystify-flask-app-secret-key

This secret key is also used to sign JWTs. JWTs signed with the HS256 algorith (the default),
must have a key of at least 32 characters long. The same key must also be passed to Hasura
as part of the ``HASURA_GRAPHQL_JWT_SECRET`` variable. See ``hasura/README.md``.
"""

SQLALCHEMY_TRACK_MODIFICATIONS = False
""" Turn this off to prevent warnings. """

TESTING = False
""" Special mode for running tests. """

WTF_CSRF_ENABLED = True
"""
Cross Site Request Forgery (CSRF) on forms, disable when testing.
Not needed on API, to be removed with Flask app removal.
"""

FLASK_SKIP_DOTENV = True
"""
If :mod:`python-dotenv` is installed, Flask will by default use it to find .env files and
use the contents of those files as environmental variables. It uses :func:`dotenv.find_dotenv`,
which keeps searching up the directory tree until it finds a .env file.

Unfortunately, flask also makes the idiotic assumption that when a .env file is found, it must
be in the root of the project and will change the working directory to that. As a consequence,
``flask db ...`` will look for ``migrations/alembic.ini`` in wherever the .env file is located,
which may not be correct at all.

This setting prevents such stupid behaviour.
"""

AWS_SNS_REGION = 'us-west-1'
"""
Our default AWS region is "us-east-2", but SNS is not available in that region. It is now set
up in this alternate region.
"""