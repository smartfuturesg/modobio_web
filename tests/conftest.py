from datetime import datetime, timedelta
import pathlib
import uuid
import pytest
import subprocess
import sys

import boto3
import twilio

from flask.json import dumps
from flask_migrate import upgrade
from sqlalchemy import select, text
from sqlalchemy.exc import ProgrammingError
from twilio.base.exceptions import TwilioRestException

from odyssey import create_app, db
from odyssey.api.client.models import ClientClinicalCareTeam, ClientClinicalCareTeamAuthorizations
from odyssey.api.lookup.models import LookupClinicalCareTeamResources
from odyssey.api.payment.models import PaymentMethods
from odyssey.api.telehealth.models import TelehealthBookings
from odyssey.api.user.models import User, UserLogin
from odyssey.integrations.twilio import Twilio
from odyssey.utils.misc import grab_twilio_credentials
from odyssey.utils.errors import MissingThirdPartyCredentials
from odyssey.utils import search

from .utils import login

# From database/0001_seed_users.sql
STAFF_ID = 12   # staff@modobio.com
CLIENT_ID = 22  # client@modobio.com

# For care team fixture
USER_TM = 'test_team_member_user@modobio.com'
NON_USER_TM = 'test_team_member_non_user@modobio.com'

def setup_db(app):
    """ Set up the database for testing.

    Runs flask-migrate and database/sql_scriptrunner.py.
    """
    # Make sure we start with an empty database.
    clear_db()

    # Flask-migrate
    root = pathlib.Path(__file__).parent.parent
    migrations = root / 'migrations'

    try:
        upgrade(directory=migrations)
    except:
        pytest.exit('Failed to run flask-migrate during test setup')

    # Load SQL scripts.
    runner = root / 'database' / 'sql_scriptrunner.py'
    cmd = [sys.executable, runner, '--db_uri', app.config['SQLALCHEMY_DATABASE_URI']]

    proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True)

    if proc.returncode != 0:
        pytest.exit(f'Database scripts failed to run: {proc.stderr}')

    # Sending output to stderr, because that is where flask-migrate sends debug/info output.
    print(proc.stdout, file=sys.stderr)

    # For general testing pusposes, give 'staff@modobio.com' all roles.
    # To test access for specific roles, use different staff users from the seeded list.
    db.session.execute(text(f'DELETE FROM "StaffRoles" WHERE user_id = {STAFF_ID};'))

    roles = db.session.execute(text('SELECT role_name FROM "LookupRoles";')).scalars().all()
    tmpl = """
        INSERT INTO "StaffRoles"
        (user_id, role, granter_id)
        VALUES
        ({}, '{}', 1);"""
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
            tc.client_pass = '123'
            tc.client_auth_header = login(tc, client, password='123')

            tc.staff = staff
            tc.staff_id = staff.user_id
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

# Used by tests in client/ and in doctor/
@pytest.fixture(scope='module')
def care_team(test_client):
    """ Add team members to client.

    Adds a team member who is staff, a team member who is a client,
    and a team members who is not a registered user.

    There is currently only 1 client user in the seeded users, but that
    is our main test client to whom we are adding team members, so a
    new temporary user will be created for this purpose.

    This yields:

    - test_client.client: owner of care team
    - care team:
        - pro@modobio.com: existing staff member added in seed users
        - name@modobio.com: existing staff member added in seed users
        - test_client.staff: existing staff member, added here
        - test_team_member_user@modobio.com: new client user, added here
        - test_team_member_non_user@modobio.com: new team member who is not a modobio user, added here

    After the fixture returns from the yield, the team members who
    were added here will be deleted. The team members who were added
    in the seed users will be left alone.

    Yields
    ------
    dict
        Dictionary containing a user_id and modobio_id for each of the newly
        addded team members:
        - staff_id
        - staff_modobio_id
        - client_id
        - client_modobio_id
        - non_user_id (no non_user_modobio_id)

    Notes
    -----

    This fixture is entire done with database interaction. It does not make use of
    API calls. This leaves off a layer of complexity that is properly tested in
    the tests.
    """
    # Create a new client user.
    tm_client = User(
        email = USER_TM,
        firstname = 'Team',
        lastname = 'Member',
        phone_number = '9871237766',
        modobio_id = 'ABC123X7Y8Z9',
        is_staff = False,
        is_client = True,
        email_verified = True)

    test_client.db.session.add(tm_client)
    test_client.db.session.commit()

    tm_login = UserLogin(user_id=tm_client.user_id)
    tm_login.set_password('password')

    test_client.db.session.add(tm_login)
    test_client.db.session.commit()

    # Add non-user as non-login user.
    tm_non_user = User(
        email=NON_USER_TM,
        is_staff=False,
        is_client=False)

    test_client.db.session.add(tm_non_user)
    test_client.db.session.commit()

    # Add members to care team
    ccteam = []
    for tm_id in (test_client.staff_id, tm_client.user_id, tm_non_user.user_id):
        cct = ClientClinicalCareTeam(
            user_id=test_client.client_id,
            team_member_user_id=tm_id)
        ccteam.append(cct)

    test_client.db.session.add_all(ccteam)

    # Add authorizations for staff member.
    resource_ids = (test_client.db.session.execute(
        select(LookupClinicalCareTeamResources.resource_id))
        .scalars()
        .all())

    ccteam_auth = []
    for resource_id in resource_ids:
        cct_auth = ClientClinicalCareTeamAuthorizations(
            user_id=test_client.client_id,
            team_member_user_id=test_client.staff_id,
            resource_id=resource_id,
            status='accepted')
        ccteam_auth.append(cct_auth)

    test_client.db.session.add_all(ccteam_auth)
    test_client.db.session.commit()

    # Return user_ids and modobio_ids
    yield {
        'staff_id': test_client.staff_id,
        'staff_modobio_id': test_client.staff.modobio_id,
        'client_id': tm_client.user_id,
        'client_modobio_id': tm_client.modobio_id,
        'non_user_id': tm_non_user.user_id}

    # Before we can delete care team members and authorizations,
    # refetch them. Tests may have already deleted them.

    # Delete authorizations
    ccteam_auth = (test_client.db.session.execute(
        select(ClientClinicalCareTeamAuthorizations)
        .filter_by(
            team_member_user_id=test_client.staff_id))
        .scalars()
        .all())

    for cct_auth in ccteam_auth:
        test_client.db.session.delete(cct_auth)

    # Delete care team
    ccteam = (test_client.db.session.execute(
        select(ClientClinicalCareTeam)
        .where(
            ClientClinicalCareTeam.team_member_user_id.in_((
                test_client.staff_id,
                tm_client.user_id,
                tm_non_user.user_id))))
        .scalars()
        .all())

    for cct in ccteam:
        test_client.db.session.delete(cct)

    # Delete temp users
    test_client.db.session.delete(tm_non_user)
    test_client.db.session.delete(tm_client)
    test_client.db.session.commit()



# Used by tests in client/ and in doctor/
@pytest.fixture(scope='module')
def telehealth_booking(test_client, wheel = False):
    """ 
    Create a new telehealth booking between one of the wheel test users and client user 22

    Yields
    ------
    TelehealthBookings obj        

    """

    # prepare a payment method to be used
    pm = PaymentMethods(
        payment_id = '123456789',
        payment_type = 'VISA',
        number = 123,
        expiration = '05/26',
        is_default = True,
        user_id = 22
    )

    test_client.db.session.add(pm)
    test_client.db.session.flush()


    # # make a telehealth booking by direct db call
    target_date = datetime.now() + timedelta(days=1)

    booking = TelehealthBookings(
        staff_user_id = 30 if wheel else 1,
        client_user_id = 22,
        target_date = target_date.date(),
        booking_window_id_start_time = 1,
        booking_window_id_end_time = 4,
        booking_window_id_start_time_utc = 1,
        booking_window_id_end_time_utc = 4,
        client_location_id = 1,
        payment_method_id = pm.idx,
        external_booking_id = uuid.uuid4()
    )

    
    
    test_client.db.session.add(booking)
    test_client.db.session.flush()

    # add booking transcript
    twilio = Twilio()
    conversation_sid = twilio.create_telehealth_chatroom(booking.idx)

    yield booking

    # delete chatroom and booking
    test_client.db.session.delete(booking)
    try:
        twilio.delete_conversation(conversation_sid)
    except TwilioRestException:
        # conversation was already removed as part of a test
        pass