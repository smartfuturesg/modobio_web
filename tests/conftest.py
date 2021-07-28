import base64
import copy
import pathlib
import pytest
import subprocess
import sys

from datetime import datetime

import boto3
import twilio

from flask_migrate import upgrade
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.sql.expression import select

from odyssey import create_app, db

from odyssey.api.user.models import User
from odyssey.utils.constants import ACCESS_ROLES
from odyssey.utils.misc import grab_twilio_credentials
from odyssey.utils.errors import MissingThirdPartyCredentials
from odyssey.utils import search

from .utils import login

# From database/0001_seed_users.sql
STAFF_ID = 12   # staff@modobio.com
CLIENT_ID = 22  # client@modobio.com

pytest._migrated = False
pytest._sqlloaded = False

def setup_db(app):
    """ Set up the database for testing.

    Runs flask-migrate and database/sql_scriptrunner.py.
    """
    # Make sure we start with an empty database.
    clear_db()

    # Flask-migrate
    root = pathlib.Path(__file__).parent.parent
    migrations = root / 'migrations'
    if not pytest._migrated:
        try:
            upgrade(directory=migrations)
        except:
            pytest.exit('Failed to run flask-migrate during test setup')

        pytest._migrated = True

    # Load SQL scripts.
    runner = root / 'database' / 'sql_scriptrunner.py'
    cmd = [sys.executable, runner, '--db_uri', app.config['SQLALCHEMY_DATABASE_URI']]

    if not pytest._sqlloaded:
        proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True)

        if proc.returncode != 0:
            pytest.exit(f'Database scripts failed to run: {proc.stderr}')

        # Sending output to stderr, because that is where flask-migrate sends debug/info output.
        print(proc.stdout, file=sys.stderr)
        pytest._sqlloaded = True

    # For general testing pusposes, give 'staff@modobio.com' all roles.
    # To test access for specific roles, use different staff users from the seeded list.
    db.session.execute(text(f'DELETE FROM "StaffRoles" WHERE user_id = {STAFF_ID};'))

    roles = db.session.execute(text('SELECT role_name FROM "LookupRoles";')).scalars().all()
    tmpl = """
        INSERT INTO "StaffRoles"
        (user_id, role, verified)
        VALUES
        ({}, '{}', 't');"""
    insert = [tmpl.format(STAFF_ID, role) for role in roles]
    db.session.execute(text(' '.join(insert)))
    db.session.commit()

    # Add elastic search index
    search.build_ES_indices()

def clear_db():
    """ Delete all tables in the database. """

    tables = (db.session.execute(
        text("""
            SELECT table_name, table_type
            FROM information_schema.tables 
            WHERE table_schema = 'public';"""))
        .all())

    for table, table_type in tables:
        if table_type == 'BASE TABLE':
            table_type = 'TABLE'

        try:
            db.session.execute(text(f'DROP {table_type} "{table}" CASCADE;'))
        except ProgrammingError as err:
            # Sqlalchemy wraps dialect errors in more generic errors.
            # Here: psycopg2.errors.UndefinedTable -> sqlalchemy.exc.ProgrammingError
            if 'does not exist' in str(err.orig):
                # Table already deleted through cascase.
                db.session.rollback()
                continue
            else:
                raise err
        finally:
            db.session.commit()

def clear_twilio(modobio_ids=None):
    """ Delete all Twilio conversations. """
    if not modobio_ids:
        modobio_ids = db.session.execute(select(User.modobio_id)).scalars().all()

    try:
        twilio_credentials = grab_twilio_credentials()
    except MissingThirdPartyCredentials:
        return

    client = twilio.rest.Client(
        twilio_credentials['api_key'], 
        twilio_credentials['api_key_secret'],
        twilio_credentials['account_sid'])

    for modobio_id in modobio_ids:
        try:
            client.conversations.users(modobio_id).delete()
        except twilio.rest.TwilioException:
            # User does not exist in Twilio
            continue

@pytest.fixture(scope='session')
def test_client():
    """ Flask application instance for testing. """
    app = create_app()

    with app.test_client() as tc:
        with app.app_context():
            # At this point 'tc' is a live app, so we can call
            # functions that rely on Flask functionality.
            setup_db(app)

            # Load the main users for testing
            client = db.session.query(User).filter_by(user_id=CLIENT_ID).one_or_none()
            staff = db.session.query(User).filter_by(user_id=STAFF_ID).one_or_none()

            # Add everything we want to pass to tests
            # into the test_client instance as parameters.
            tc.db = db

            tc.client = client
            tc.client_id = client.user_id
            tc.client_email = client.email
            tc.client_pass = '123'
            tc.client_auth_header = login(tc, client, password='123')

            tc.staff = staff
            tc.staff_id = staff.user_id
            tc.staff_email = staff.email
            tc.staff_pass = '123'
            tc.staff_auth_header = login(tc, staff, password='123')

            yield tc

            # Cleanup functions also need a live app.
            db.session.rollback()
            clear_twilio()
            clear_db()

            # https://stackoverflow.com/questions/26350911/what-to-do-when-a-py-test-hangs-silently
            db.session.close()

    # Delete files from S3 bucket
    if not app.config['AWS_S3_PYTEST_KEEP']:
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(app.config['AWS_S3_BUCKET'])

        objects = bucket.objects.filter(Prefix=app.config['AWS_S3_PREFIX'])
        objects = [{'Key': obj.key} for obj in objects]
        if objects:
            delete = {
                'Objects': objects,
                'Quiet': True}
            bucket.delete_objects(Delete=delete)
