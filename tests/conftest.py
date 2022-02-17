import os
import pathlib
import uuid
from bson import ObjectId
import pytest
import subprocess
import sys
import uuid

from datetime import datetime, timedelta

import boto3
import twilio

from flask import g
from flask_migrate import upgrade
from sqlalchemy import select, text
from sqlalchemy.exc import ProgrammingError
from twilio.base.exceptions import TwilioRestException
from werkzeug.exceptions import BadRequest

from odyssey import create_app, db, mongo
from odyssey.api.client.models import ClientClinicalCareTeam
from odyssey.api.lookup.models import LookupBookingTimeIncrements
from odyssey.api.payment.models import PaymentMethods
from odyssey.api.telehealth.models import TelehealthBookings, TelehealthChatRooms
from odyssey.api.user.models import User, UserLogin
from odyssey.integrations.twilio import Twilio
from odyssey.utils import search

# import fixtures from telehealth
# from tests.functional.telehealth.conftest import *

from .utils import login

# See database/1000_staff_all_roles.sql and database/3000_client.sql
STAFF_EMAIL = 'name@modobio.com'
CLIENT_EMAIL = 'client@modobio.com'

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

    proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True, env=os.environ)

    if proc.returncode != 0:
        pytest.exit(f'Database scripts failed to run: {proc.stderr}')

    # Sending output to stderr, because that is where flask-migrate sends debug/info output.
    print(proc.stdout, file=sys.stderr)

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
    twilio_obj = Twilio()
    if not modobio_ids:
        modobio_ids = db.session.execute(select(User.modobio_id)).scalars().all()

    try:
        twilio_credentials = twilio_obj.grab_twilio_credentials()
    except BadRequest:
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
            client = db.session.query(User).filter_by(email=CLIENT_EMAIL).one_or_none()
            staff = db.session.query(User).filter_by(email=STAFF_EMAIL).one_or_none()

            # Add everything we want to pass to tests
            # into the test_client instance as parameters.
            tc.db = db

            tc.mongo = mongo

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
        - staff_id (for name@modobio.com)
        - staff_modobio_id
        - client_id
        - client_modobio_id
        - non_user_id
        - non_user_modobio_id (always None)

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
        was_staff = False,
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
        was_staff=False,
        is_client=False)

    test_client.db.session.add(tm_non_user)
    test_client.db.session.commit()

    # Add members to care team
    ccteam = []
    for tm_id in (tm_client.user_id, tm_non_user.user_id):
        cct = ClientClinicalCareTeam(
            user_id=test_client.client_id,
            team_member_user_id=tm_id)
        ccteam.append(cct)

    test_client.db.session.add_all(ccteam)
    test_client.db.session.commit()

    # Return user_ids and modobio_ids
    yield {
        'staff_id': test_client.staff_id,
        'staff_modobio_id': test_client.staff.modobio_id,
        'client_id': tm_client.user_id,
        'client_modobio_id': tm_client.modobio_id,
        'non_user_id': tm_non_user.user_id,
        'non_user_modobio_id': None}

    # Before we can delete care team members and authorizations,
    # refetch them. Tests may have already deleted them.

    # Delete care team
    ccteam = (test_client.db.session.execute(
        select(ClientClinicalCareTeam)
        .where(
            ClientClinicalCareTeam.team_member_user_id.in_((
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



@pytest.fixture(scope='function')
def booking_function_scope(test_client):
    """ Create a new telehealth booking.

    This bookings fixture is used in the Twilio section of testing.
    The Telehealth section has its own bookings fixture.

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
        user_id = test_client.client_id
    )

    test_client.db.session.add(pm)
    test_client.db.session.flush()

    # simulates logged-in user accepting a booking. Necessary to satisfy background process: telehealth.models.add_booking_status_history
    g.flask_httpauth_user = (test_client.staff, UserLogin.query.filter_by(user_id = test_client.staff_id).one_or_none())

    # make a telehealth booking by direct db call
    # booking is made less than 10 minutes out from the current time
    target_datetime = datetime.utcnow() #+ timedelta(hours=TELEHEALTH_BOOKING_LEAD_TIME_HRS)

    # Round target_datetime up to the next 10-minute time.
    target_datetime = target_datetime - timedelta(
        minutes=target_datetime.minute % 10 - 10,
        seconds=target_datetime.second,
        microseconds=target_datetime.microsecond)

    time_inc = LookupBookingTimeIncrements.query.all()
        
    start_time_idx_dict = {item.start_time.isoformat() : item.idx for item in time_inc} # {datetime.time: booking_availability_id}
    
    booking_start_idx = start_time_idx_dict.get(target_datetime.time().strftime('%H:%M:%S'))

    # below is to account for bookings starting at the very end of the day so that the booking end time
    # falls on the following day
    if time_inc[-1].idx - (booking_start_idx + 3) < 0:
        booking_end_idx = abs(time_inc[-1].idx - (booking_start_idx + 3))
    else:
        booking_end_idx = booking_start_idx + 3

    booking = TelehealthBookings(
        staff_user_id = test_client.staff_id,
        client_user_id = test_client.client_id,
        target_date = target_datetime.date(),
        target_date_utc = target_datetime.date(),
        booking_window_id_start_time = booking_start_idx,
        booking_window_id_end_time = booking_end_idx,
        booking_window_id_start_time_utc = booking_start_idx,
        booking_window_id_end_time_utc = booking_end_idx,
        client_location_id = 1,  # TODO: make this not hardcoded
        payment_method_id = pm.idx,
        external_booking_id = uuid.uuid4()
    )

    test_client.db.session.add(booking)
    test_client.db.session.flush()

    # add booking transcript
    twilio = Twilio()
    conversation_sid = twilio.create_telehealth_chatroom(booking.idx)

    test_client.db.session.commit()

    yield booking

    # delete chatroom, booking, and payment method
    chat_room = test_client.db.session.execute(select(TelehealthChatRooms).where(TelehealthChatRooms.booking_id == booking.idx)).scalars().one_or_none()
    
    # remove transcript from mongo db
    if chat_room.transcript_object_id:
        test_client.mongo.db.telehealth_transcripts.find_one_and_delete({"_id": ObjectId(chat_room.transcript_object_id)})

    for status in booking.status_history:
        test_client.db.session.delete(status)
        
    test_client.db.session.delete(chat_room)
    test_client.db.session.delete(booking)
    test_client.db.session.flush()
    
    test_client.db.session.delete(pm)
    test_client.db.session.commit()
    try:
        twilio.delete_conversation(conversation_sid)
    except TwilioRestException:
        # conversation was already removed as part of a test
        pass
