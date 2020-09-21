# Configuration defaults
# This file is imported by config.py, so should be valid Python
import tempfile

# Do all local development
FLASK_DEV = 'local'

# Storage location for PDF documents
DOCS_BUCKET_NAME = tempfile.TemporaryDirectory().name

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

# Testing
TESTING = False
WTF_CSRF_ENABLED = True
