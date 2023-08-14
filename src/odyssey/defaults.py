"""Configuration defaults

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

API_VERSION = ''
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

If not set, it will default to DEBUG if FLASK_DEBUG=true and AUDIT otherwise.
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

This prefix will be prepended to **every file** stored in the bucket.

There is only one S3 bucket for development. To prevent multiple developers from
interfering with each other, this prefix will be set to the local username during
development.

There is a special prefix "temp". The buckets are configured to delete anything
in "temp" automatically after 24 hours.

When pytest is run, the prefix will be set to "temp/pytest-xxxxxx", where xxxxxx
is a random 6-digit hex string. Pytest should delete this prefix when finished,
but sometimes this does not happen (e.g. when pytest is interrupted or when
:const:`AWS_S3_PYTEST_KEEP` is set). In that case, the files are still deleted
after 24 hours because they are in temp/.

When defining ``AWS_S3_PREFIX``, do **not** add leading or trailing /.

.. seealso:: :const:`AWS_S3_USER_PREFIX`
             :const:`AWS_S3_PYTEST_KEEP`
             :mod:`odyssey.utils.files`
"""

AWS_S3_USER_PREFIX = 'id{user_id:05d}'
""" User specific prefix (path) for files in the AWS S3 bucket.

This prefix will be **appended after** :const:`AWS_S3_PREFIX` and is
specific for each user. It must hold a string formatting template
that will be formatted with ``user_id``.

The full prefix as used in :mod:`odyssey.utils.files` is:

.. code:: python

    prefix = AWS_S3_PREFIX + '/' + AWS_S3_USER_PREFIX.format(user_id=user_id)

:attr:`~odyssey.utils.files.FileUpload.prefix` will be prepended to every
file uploaded through :class:`odyssey.utils.files.FileUpload`.

.. seealso:: :const:`AWS_S3_PREFIX` and :mod:`odyssey.utils.files`
"""

AWS_S3_PYTEST_KEEP = False
""" Keep files on AWS S3 after a pytest run.

Set this to True (default is False) to keep files on AWS S3 after a pytest run ends.
This may be useful to debug tests in combination with file uploads.

Note that files will be kept for only 24 hours after a pytest run, unless
:const:`AWS_S3_PREFIX` is changed to something outside of temp/.

.. seealso:: :const:`AWS_S3_PREFIX`
"""
# TODO Telehealth on the Shelf - removed twilio access key defaults - should be added back when we
# reactivate a Twilio enabled telehealth feature.

# Twilio settings
# TWILIO_ACCOUNT_SID = ''
""" Twilio account ID number. """

# TWILIO_API_KEY_SID = ''
""" Twilio API access key ID number. """

# TWILIO_API_KEY_SECRET = ''
""" Twilio API access key secret. """

# CONVERSATION_SERVICE_SID = ''
""" Twilio conversation serive ID number. """

TELEHEALTH_BOOKING_LEAD_TIME_HRS = 2
""" Telehealth booking lead time.

This config variable represents the minimum amount of time between making a
booking and the start of the booking. Will be set to 0 for debug and testing.
"""

TELEHEALTH_BOOKING_TRANSCRIPT_EXPIRATION_HRS = 336
""" Telehealth booking edit time.

Booking transcripts can be edited after the booking starts. This config variable
sets the maximum time in hours, from the start of the booking, when editing is
still possible. Will be set to 0.5 for debug and testing.
"""

TELEHEALTH_BOOKING_DURATION = 30
""" Telehealth booking duration.

The default telehealth duration in minutes.
"""

# Celery settings.
CELERY_BROKER_URL = 'redis://localhost:6379/0'
""" Celery default broker URL.

This must be a URL in the form of: ``transport://userid:password@hostname:port/virtual_host``

This variable will be converted to ``broker_url`` (lower case) to work with
Celery's new config system.
"""

CELERY_RESULT_BACKEND = ''
""" Celery default backend to store results.

The backend used to store task results (tombstones).

This variable will be converted to ``result_backend`` (lower case) to work with
Celery's new config system.
"""

CELERY_REDBEAT_REDIS_URL = CELERY_BROKER_URL
""" Celery-redbeat will use redis to store a persistent celerybeat schedule

This variable will be converted to ``redbeat_redis_url`` (lower case) to work with
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
INSTAMED_MERCHANT_ID = ''
"""InstaMed Merchant ID."""

INSTAMED_API_KEY = ''
""" InstaMed API access key ID number. """

INSTAMED_API_SECRET = ''
""" InstaMed API access key secret. """

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
GOOGLE_RECAPTCHA_SECRET = ''

WEARABLES_DYNAMO_TABLE = 'Wearables-V1-dev-r1-3-1'
""" Name of the table in AWS DynamoDB where wearables data is stored.

.. deprecated:: 1.3.1
    With Terra integration in release 1.3.1, AWS Dynamo will no longer be used.

The table name is versioned to allow multiple versions of the API to run
at the same time. Make sure to update this value when moving to a new
branch.
"""

WEARABLE_DATA_DEFAULT_RANGE_DAYS = 14
""" Default date range for wearable data.

When no date range is specified when requesting wearable data,
this many days of data is returned.
"""

# Apple app store
APPLE_APPSTORE_API_KEY = ''

APPLE_APPSTORE_API_KEY_ID = 'C9PC58MRPT'
"""Identifier for the API key"""

APPLE_APPSTORE_ISSUER_ID = 'a81919e2-a4c0-4611-b8d0-7b260a6fdd62'
"""ID from appstore conenct account"""

APPLE_APPSTORE_BUNDLE_ID = 'com.modobio.ModoBioClient'

APPLE_APPSTORE_BASE_URL = 'https://api.storekit-sandbox.itunes.apple.com'

MAINTENANCE_DYNAMO_TABLE = 'dev_maintenance_v02'

MAINTENANCE_REASONS_TABLE = 'prod_maintenance_reasons'

MAINTENANCE_TIMEZONE = 'UTC'

# Maintenance Business Hours Time Window In UTC
BUSINESS_HRS_START = 13

BUSINESS_HRS_END = 6

# Maintenance Notice Periods (in days)
MAINT_SHORT_NOTICE = 2

MAINT_STD_NOTICE = 14

SERVER_NAME = '127.0.0.1:5000'
"""
Name and port number of the server. This setting allows for
url generation outside of the Flask request context. This is useful for
creating urls as part of celery tasks. 
"""

# Active Campaign
ACTIVE_CAMPAIGN_BASE_URL = 'https://modobio.api-us1.com/api/3/'
ACTIVE_CAMPAIGN_LIST = ''
ACTIVE_CAMPAIGN_API_KEY = ''

TERRA_DEV_ID = ''
"""
Developer ID for Terra API.

There are three environments: testing, staging, and production.
Each environment has its own developer ID, API key, and secret.
The URL for the webhook must be set in the developer dashboard,
which is also the place where id, key, and secret can be found.
https://dashboard.tryterra.co/terraapi/customise
"""

TERRA_API_KEY = ''
"""
Key for Terra API.

See :const:`TERRA_DEV_ID`
"""

TERRA_API_SECRET = ''
"""
Secret password for Terra API.

See :const:`TERRA_DEV_ID`
"""

SUBSCRIPTION_UPDATE_FREQUENCY_MINS = 5
"""Controls how often to run the subscription update periodic task.

:type: int
"""

GOOGLE_JSON_KEY_PATH = ''
"""Path to the Google service account JSON key file.

This file is used to authenticate with Google APIs.

:type: str
"""

GOOGLE_SERVICE_ACCOUNT_KEY = {}
"""Google service account key.

This is the parsed JSON key file.

:type: dict
"""

GOOGLE_PACKAGE_NAME = 'com.modobio.modobioclient'
"""
Package name for android app. 

:type: str
"""
