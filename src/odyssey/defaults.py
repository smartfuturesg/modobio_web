# Configuration defaults
# This file is imported by config.py, so should be valid Python
import tempfile

# Do all local development
FLASK_DEV = 'local'

# File storage location
# This directory is **NOT** deleted by the program.
# However, using tempfile.TemporaryDirectory() went out of scope
# and was therefore deleted after defaults was loaded, but while
# Flask was still running.
S3_BUCKET_NAME = tempfile.mkdtemp()

# Whooshee fulltext index, persist location.
# Defaults to 'whooshee' in local dir
WHOOSHEE_DIR = None

# Database
DB_FLAV = 'postgresql'
DB_USER = ''
DB_PASS = ''
DB_HOST = 'localhost'
DB_NAME = 'modobio'

# Oura Cloud OAuth parameters
OURA_CLIENT_ID = ''
OURA_CLIENT_SECRET = ''
OURA_AUTH_URL = 'https://cloud.ouraring.com/oauth/authorize'
OURA_TOKEN_URL = 'https://api.ouraring.com/oauth/token'

# Flask app secret key
SECRET_KEY = 'dev'

# SQLAlchemy settings
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Enable/disable swagger documentation
SWAGGER_DOC = True

# Testing
TESTING = False
WTF_CSRF_ENABLED = True
