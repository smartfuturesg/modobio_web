""" Configuration defaults

This file defines the configuration defaults for the entire API. It is loaded by
:mod:`odyssey.config`.
"""
# This file is imported by config.py, so it must be valid Python.

# General defaults
SECRET_KEY = 'abcdefghijklmnopqrstuvwxyz0123456789'
"""
Flask secret key, used to encrypt sessions amongst other things.
See https://stackoverflow.com/questions/22463939/demystify-flask-app-secret-key

This secret key is also used to sign JWTs. JWTs signed with the HS256 algorith (the default),
must have a key of at least 32 characters long. The same key must also be passed to Hasura
as part of the ``HASURA_GRAPHQL_JWT_SECRET`` variable. See ``hasura/README.md``.
"""

API_VERSION = 'unknown version'
"""
Version number of the API.

Can be set by the environment (like all other parameters) or by running ``python setup.py build``,
which calls :mod:`setuptools_scm`. The latter created a file ``odyssey/version.py``. This is
relevant for pip installation of the API.
"""

SQLALCHEMY_TRACK_MODIFICATIONS = False
"""
Turn this off to prevent warnings.

https://stackoverflow.com/questions/33738467/how-do-i-know-if-i-can-disable-sqlalchemy-track-modifications/33790196#33790196
"""

TESTING = False
"""
Special mode for running tests. There is usually no need to set this manually, it will
be set to True when running pytest.
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

LOG_LEVEL = ''
""" Show log message of this level and higher.

Accepted levels are:
DEBUG, INFO, AUDIT, WARNING, ERROR, CRITICAL, or any integer.

If not set, it will default to DEBUG if FLASK_ENV=development and AUDIT otherwise.
"""

LOG_FORMAT_JSON = False
""" Output logs in JSON format.

By default, logging prints pre-formatted strings. This switch enables JSON output for logs,
which is useful for AWS CloudTrail integration.
"""

# Database parameters
DB_FLAV = 'postgresql'
""" Database "flavour" or dialect. """

DB_USER = ''
""" Username for database. """

DB_PASS = ''
""" Password for database. """

DB_HOST = 'localhost'
""" Hostname for database. """

DB_NAME = 'modobio'
""" Name of database. """

DB_NAME_TESTING = 'modobio_test'
""" Name of database specifically for running pytest. """

DB_URI = ''
""" Set the database URI as a single string. Takes precedence over setting the parts. """

# Elasticsearch
ELASTICSEARCH_URL = 'http://localhost:9200'
""" URL of the local elasticsearch instance. """

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

# AWS settings
AWS_SNS_REGION = 'us-west-1'
"""
Our default AWS region is "us-east-2", but SNS is not available in that region.
Instead, it uses this alternate region.
"""

AWS_S3_BUCKET = 'local-dev-393511634479'
""" Name of the AWS S3 bucket where files are stored. """

AWS_S3_PREFIX = ''
""" Prefix (path) of files in the AWS S3 bucket.

There is only one S3 bucket for development. To prevent multiple developers from
interfering with each other, the prefix will be set to the local username during
development. When not in development (production environment), the prefix will
be empty.

When pytest is run, the prefix will be set to "pytest-xxxxxx", where xxxxxx is a
random 6-digit hex string. Pytest should delete this prefix when finished.

Finally, prefix can be set to "temp". The buckets are configured to delete anything
in "temp" automatically after 24 h.

Set ``export AWS_S3_PREFIX=none`` in the environment to force an empty prefix, even
during development and testing.

When defining ``AWS_S3_PREFIX``, do **not** using leading or trailing /.
"""

AWS_S3_PYTEST_KEEP = False
""" Keep files on AWS S3 after a pytest run.

Set this to True (default is False) to keep files on AWS S3 after a pytest run ends.
This may be useful to debug tests in combination with file uploads.
"""

# Twilio settings
TWILIO_ACCOUNT_SID = ''
""" Twilio account ID number. """

TWILIO_API_KEY_SID = ''
""" Twilio API access key ID number. """

TWILIO_API_KEY_SECRET = ''
""" Twilio API access key secret. """

CONVERSATION_SERVICE_SID = ''
""" Twilio conversation serive ID number. """

# Celery settings.
CELERY_BROKER_URL = 'redis://localhost:6379/0'
""" Celery default broker URL.

This must be a URL in the form of: ``transport://userid:password@hostname:port/virtual_host``

This variable will be converted to ``broker_url`` (lower case) to work with
Celery's new config system.
"""

CELERY_RESULT_BACKEND = CELERY_BROKER_URL
""" Celery default backend to store results.

The backend used to store task results (tombstones).

This variable will be converted to ``result_backend`` (lower case) to work with
Celery's new config system.
"""

CELERY_ENABLE_UTC = True
""" Celery timezone.

If enabled dates and times in messages will be converted to use the UTC timezone.

Note that workers running Celery versions below 2.5 will assume a local timezone
for all messages, so only enable if all workers have been upgraded.

This variable will be converted to ``enable_utc`` (lower case) to work with
Celery's new config system.
"""

# InstaMed Settings
INSTAMED_API_KEY = ''
""" InstaMed API access key ID number. """

INSTAMED_API_SECRET = ''
""" InstaMed API access key secret. """

# Dosespot Settings
DOSESPOT_API_KEY = ''
""" DoseSpot API access key ID number. """

DOSESPOT_MODOBIO_ID = ''
""" DoseSpot ModoBio ID. """

DOSESPOT_ENCRYPTED_MODOBIO_ID = ''

DOSESPOT_ADMIN_ID = ''
""" DoseSpot Admin ID"""

DOSESPOT_ENCRYPTED_ADMIN_ID = ''

DOSESPOT_PROXY_USER_ID = '238851'

DOSESPOT_BASE_URL = 'https://my.staging.dosespot.com'

# Wheel settings
WHEEL_API_TOKEN = ''
WHEEL_MD_CONSULT_RATE = '7161c1e9-69a6-4430-a7ef-04593300f48a'
WHEEL_NP_CONSULT_RATE = '9c36e5c6-ed91-4546-a847-c649c81db265'

# mongo db
MONGO_URI = ''

# Calling host base uri 
FRONT_END_DOMAIN_NAME = ''
""" Default name of calling domain

The purpose of the variable is to produce clickable URLs specific to the domain being used
ie. production (modobio.com), dev r7 (dev-r0-7.modobio.com) 
"""

# Google ReCaptcha api secret
GOOGLE_RECAPTCHA_SECRET = ""

WEARABLES_DYNAMO_TABLE = 'Wearables-V1-dev'

# Apple app store 
APPLE_APPSTORE_API_KEY_FILE = '' 

APPLE_APPSTORE_API_KEY_ID = 'C9PC58MRPT'
"""Identifier for the API key"""

APPLE_APPSTORE_ISSUER_ID = 'a81919e2-a4c0-4611-b8d0-7b260a6fdd62'
"""ID from appstore conenct account"""

APPLE_APPSTORE_BUNDLE_ID = 'com.modobio.ModoBioClient'

APPLE_APPSTORE_BASE_URL = 'https://api.storekit-sandbox.itunes.apple.com'

