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

# Whooshee fulltext index, persist location.
# Defaults to 'whooshee' in local dir
WHOOSHEE_DIR = None
""" Directory where whooshee stores persistent index. Defaults to local directory if unset. """

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

SECRET_KEY = 'dev'
"""
Flask secret key, used to encrypt sessions amongst other things.
See https://stackoverflow.com/questions/22463939/demystify-flask-app-secret-key
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

TELEHEALTH_SESSION_DURATION = 30
TELEHEALTH_BOOKING_NOTICE_WINDOW = 8