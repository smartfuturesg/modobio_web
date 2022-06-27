import uuid
from bson.objectid import ObjectId
import pytest

from datetime import datetime, timedelta, timezone

from flask import g
from flask.json import dumps
from sqlalchemy import select
from twilio.base.exceptions import TwilioRestException

from odyssey.api.lookup.models import LookupBookingTimeIncrements
from odyssey.api.notifications.models import NotificationsPushRegistration
from odyssey.api.payment.models import PaymentMethods
from odyssey.api.practitioner.models import PractitionerCredentials
from odyssey.api.staff.models import StaffProfile, StaffRoles, StaffOperationalTerritories
from odyssey.api.user.models import User, UserLogin
from odyssey.api.telehealth.models import TelehealthBookings, TelehealthChatRooms, TelehealthStaffAvailability, TelehealthStaffSettings
from odyssey.integrations.twilio import Twilio
from odyssey.utils.constants import ACCESS_ROLES, DAY_OF_WEEK, TELEHEALTH_BOOKING_LEAD_TIME_HRS
from odyssey.utils.message import PushNotification

@pytest.fixture(scope='session', autouse=True)
def telehealth_clients(test_client):
    """ Generate and return client users for telehealth testing. """
    clients = []
    for i in range(10):
        client = User(
            firstname='Test',
            middlename='O.',
            lastname='Sterone',
            email=f'client{i}@example.com',
            phone_number=f'91111111{i}',
            is_staff=False,
            was_staff=False,
            is_client=True,
            email_verified=True,
            modobio_id = f'KW99TSVWP88{i}')
        test_client.db.session.add(client)
        test_client.db.session.flush()

        client_login = UserLogin(user_id=client.user_id)
        client_login.set_password('password')

        test_client.db.session.add(client_login)
        test_client.db.session.commit()

        clients.append(client)

    pytest.telehealth_clients_created = True
    return clients

@pytest.fixture(scope='session', autouse=True)
def telehealth_staff(test_client):
    """ Generate and return staff users for telehealth testing. """
    staffs = []
    for i in range(10):
        staff = User(
            firstname='Staff',
            middlename='E.',
            lastname='Stafferson',
            email=f'staff{i}@example.com',
            phone_number=f'922222222{i}',
            is_staff=True,
            was_staff=True,
            is_client=False,
            email_verified=True,
            modobio_id=f'ZW99TSVWP88{i}')

        test_client.db.session.add(staff)
        test_client.db.session.commit()

        staff_login = UserLogin(user_id=staff.user_id)
        staff_login.set_password('password')
        test_client.db.session.add(staff_login)
        consult_rate = 100.00

        staff_profile = StaffProfile(user_id = staff.user_id)
        test_client.db.session.add(staff_profile)
        test_client.db.session.commit()
        if i < 5:
            staff_role = StaffRoles(
                user_id=staff.user_id,
                role='medical_doctor',
                granter_id=1,
                consult_rate=consult_rate)
            test_client.db.session.add(staff_role)
        else:
            for role in ACCESS_ROLES:
                staff_role = StaffRoles(
                    user_id=staff.user_id,
                    role=role,
                    granter_id=1,
                    consult_rate=consult_rate)
                test_client.db.session.add(staff_role)

        test_client.db.session.commit()
        creds = []
        creds.append(PractitionerCredentials(
            user_id = staff.user_id,
            country_id = 1,
            state = 'FL',
            credential_type = 'med_lic',
            credentials = '123456789',
            status='Verified',
            role_id = StaffRoles.query.filter_by(user_id=staff.user_id, role = 'medical_doctor').one_or_none().idx
        ))

        creds.append(PractitionerCredentials(
            user_id = staff.user_id,
            country_id = 1,
            credential_type = 'npi',
            credentials = '123456789',
            status='Verified',
            role_id = StaffRoles.query.filter_by(user_id=staff.user_id, role = 'medical_doctor').one_or_none().idx
        ))
        test_client.db.session.add_all(creds)
        test_client.db.session.commit()
        staffs.append(staff)

    return staffs

@pytest.fixture(scope='session')
def payment_method(test_client):
    """ Generate a payment method, needed in telehealth testing. """
    response = test_client.post(
        f'/payment/methods/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps({
            'token': '4111111111111111',
            'expiration': '04/25',
            'cardholder_name': "Test Tester",
            'is_default': True}),
        content_type='application/json')
    pm = PaymentMethods.query.filter_by(user_id=test_client.client_id).first()

    yield pm
    # TODO: there is a tangled mess of left-over entries in TelehealthBooking,
    # TelehealthBookingStatus, chat room and more. Cascading is not working.
    # Disable clean up for now.
    # test_client.db.session.delete(pm)
    # test_client.db.session.commit()


@pytest.fixture(scope='session')
def staff_credentials(test_client):
    """ Add staff credentials for telehealth testing. """
    role = (
        StaffRoles
        .query
        .filter_by(
            user_id=test_client.staff_id,
            role='medical_doctor')
        .one_or_none())

    creds = PractitionerCredentials(
        user_id=test_client.staff_id,
        country_id=1,
        state='FL',
        credential_type='NPI',
        credentials='good doc',
        status='Verified',
        role_id=role.idx)

    test_client.db.session.add(creds)
    test_client.db.session.commit()

    yield creds
    # TODO: find where these creds are deleted, 
    # an error happens when trying to delete them here becuase they're already been deleted.
    #test_client.db.session.delete(creds)
    #test_client.db.session.commit()

@pytest.fixture(scope='session')
def staff_consult_rate(test_client):
    """ Add staff consult rate for telehealth testing. """
    role = (
        StaffRoles
        .query
        .filter_by(
            user_id=test_client.staff_id,
            role='medical_doctor')
        .one_or_none())
    
    role.consult_rate = 100.00
    test_client.db.session.commit()

    yield role

    role.consult_rate = None
    test_client.db.session.commit()    

@pytest.fixture(scope='session')
def staff_territory(test_client):
    """ Generate an operational territory for staff member, needed for telehealth testing. """
    role = (
        StaffRoles
        .query
        .filter_by(
            user_id=test_client.staff_id,
            role='medical_doctor')
        .one_or_none())

    territory = StaffOperationalTerritories(
        user_id=test_client.staff_id,
        role_id=role.idx,
        operational_territory_id=1)
    test_client.db.session.add(territory)
    test_client.db.session.commit()

    yield territory

    test_client.db.session.delete(territory)
    test_client.db.session.commit()

@pytest.fixture(scope='session', autouse=True)
def register_device(test_client):
    """ Register a dummy device for test client, needed for telehealth testing. """
    pn = PushNotification()
    device = NotificationsPushRegistration(user_id=test_client.client_id)
    device.arn = pn.register_device(
        'abc123',
        'debug',
        device_info='debug device for telehealth testing')
    device.device_token = 'abc123'
    device.device_id = 'telehealth_test'
    device.device_description = 'debug device for telehealth testing'
    test_client.db.session.add(device)

    yield device

    pn.unregister_device(device.arn)
    test_client.db.session.delete(device)
    test_client.db.session.commit()

@pytest.fixture(scope='module')
def booking(test_client, payment_method):
    """ Create a telehealth booking, needed for testing.

    This bookings fixture is used in the Telehealth section of testing.
    The Twilio section has its own bookings fixture.
    """
    # simulates logged-in user accepting a booking. Necessary to satisfy background process: telehealth.models.add_booking_status_history
    g.flask_httpauth_user = (test_client.staff, UserLogin.query.filter_by(user_id = test_client.staff_id).one_or_none())

    # make a telehealth booking by direct db call
    # booking is made with minimum lead time
    target_datetime = datetime.utcnow() + timedelta(hours=0.25)
    start_minute = target_datetime.minute + (10 - target_datetime.minute % 10) 
    target_datetime = target_datetime.replace(
        hour = target_datetime.hour + 1 if (start_minute == 60 and target_datetime.hour < 23) else target_datetime.hour,
        minute = 0 if start_minute == 60 else start_minute, 
        second=0)
    time_inc = LookupBookingTimeIncrements.query.all()
        
    start_time_idx_dict = {item.start_time.isoformat() : item.idx for item in time_inc} # {datetime.time: booking_availability_id}
    
    booking_start_idx = start_time_idx_dict.get(target_datetime.time().strftime('%H:%M:%S'))

    # below is to account for bookings starting at the very end of the day so that the booking end time
    # falls on the following day
    if time_inc[-1].idx - (booking_start_idx + 3) < 0:
        booking_end_idx = abs(time_inc[-1].idx - (booking_start_idx + 3))
    else:
        booking_end_idx = booking_start_idx + 3

    bk = TelehealthBookings(
        client_user_id=test_client.client_id,
        staff_user_id=test_client.staff_id,
        profession_type='medical_doctor',
        target_date = target_datetime.date(),
        target_date_utc = target_datetime.date(),
        booking_window_id_start_time = booking_start_idx,
        booking_window_id_end_time = booking_end_idx,
        booking_window_id_start_time_utc = booking_start_idx,
        booking_window_id_end_time_utc = booking_end_idx,
        client_location_id = 1,
        client_timezone='UTC',
        staff_timezone='UTC',
        charged=False,
        status='Accepted',
        payment_method_id = payment_method.idx,
        uid = uuid.uuid4(),
        consult_rate = 15.00
    )

    if not TelehealthStaffSettings.query.filter_by(user_id = test_client.staff_id).one_or_none():
        # Add telehealth staff settings for test staff where auto_confirm is True. 
        staff_telehealth_settings = TelehealthStaffSettings(
            timezone='UTC',
            auto_confirm = True,
            user_id = test_client.staff_id)

        test_client.db.session.add(staff_telehealth_settings)

    test_client.db.session.add(bk)

    test_client.db.session.flush()

    # add booking transcript
    twilio = Twilio()
    conversation_sid = twilio.create_telehealth_chatroom(bk.idx)

    test_client.db.session.commit()

    yield bk
    # delete chatroom, booking, and payment method
    chat_room = test_client.db.session.execute(select(TelehealthChatRooms).where(TelehealthChatRooms.booking_id == bk.idx)).scalars().one_or_none()
    
    # remove transcript from mongo db
    if chat_room.transcript_object_id:
        test_client.mongo.db.telehealth_transcripts.find_one_and_delete({"_id": ObjectId(chat_room.transcript_object_id)})

    for status in bk.status_history:
        test_client.db.session.delete(status)
        
    test_client.db.session.delete(chat_room)

    if bk.booking_details:
        test_client.db.session.delete(bk.booking_details)

    test_client.db.session.delete(bk)
    test_client.db.session.flush()
    
    test_client.db.session.commit()

    try:
        twilio.delete_conversation(conversation_sid)
    except TwilioRestException:
        # conversation was already removed as part of a test
        pass

@pytest.fixture(scope='function')
def staff_availabilities(test_client, telehealth_staff):
    """ 
    Fills up the staff availability table with 5 staff members
    """
    # clear current staff availability and telehealth settings
    test_client.db.session.query(TelehealthStaffAvailability).delete()
    test_client.db.session.query(TelehealthStaffSettings).delete()

    time_inc = LookupBookingTimeIncrements.query.all()
    availabilities = []
    staff_settings = []
    staff_ids = []
    for staff in telehealth_staff[:5]:
        staff_ids.append(staff.user_id)
        # each staff needs telehealth settings
        staff_settings.append(TelehealthStaffSettings(
            user_id = staff.user_id,
            auto_confirm=True,
            timezone = 'UTC'
        ))
        for day in DAY_OF_WEEK:
            for time_id in time_inc:
                availabilities.append(TelehealthStaffAvailability(
                    user_id=staff.user_id, 
                    day_of_week=day, 
                    booking_window_id = time_id.idx))
    test_client.db.session.add_all(staff_settings)
    test_client.db.session.add_all(availabilities)
    test_client.db.session.commit()

    yield


    # delete all entries
    test_client.db.session.query(TelehealthStaffAvailability
        ).filter(TelehealthStaffAvailability.user_id.in_(staff_ids)).delete()
    test_client.db.session.query(TelehealthStaffSettings
        ).filter(TelehealthStaffSettings.user_id.in_(staff_ids)).delete()

    test_client.db.session.query(TelehealthStaffAvailability).delete()
    test_client.db.session.query(TelehealthStaffSettings).delete()

@pytest.fixture(scope='module')
def upcoming_bookings(test_client, payment_method):
    """ Create a set of telehealth booking for the upcoming bookings task.

    This bookings fixture is used in the upcoming appointment celery section of testing.
    This fixture will create 3 bookings within the next 2 hours and 2 bookings after this time frame.
    """
    # simulates logged-in user accepting a booking. Necessary to satisfy background process: telehealth.models.add_booking_status_history
    g.flask_httpauth_user = (test_client.staff, UserLogin.query.filter_by(user_id = test_client.staff_id).one_or_none())

    intervals = [(0,30),(1,0),(1,30),(2,30),(5,0)]
    bookings = []
    for interval in intervals:
        target_datetime = datetime.now(timezone.utc) + timedelta(hours=interval[0], minutes=interval[1])
        start_minute = target_datetime.minute + (10 - target_datetime.minute % 10) 
        target_datetime = target_datetime.replace(
            hour = target_datetime.hour + 1 if (start_minute == 60 and target_datetime.hour < 23) else target_datetime.hour,
            minute = 0 if start_minute == 60 else start_minute, 
            second=0)
        time_inc = LookupBookingTimeIncrements.query.all()
        
        start_time_idx_dict = {item.start_time.isoformat() : item.idx for item in time_inc} # {datetime.time: booking_availability_id}
    
        booking_start_idx = start_time_idx_dict.get(target_datetime.time().strftime('%H:%M:%S'))

        # below is to account for bookings starting at the very end of the day so that the booking end time
        # falls on the following day
        if time_inc[-1].idx - (booking_start_idx + 3) < 0:
            booking_end_idx = abs(time_inc[-1].idx - (booking_start_idx + 3))
        else:
            booking_end_idx = booking_start_idx + 3
    
        bk = TelehealthBookings(
            client_user_id=test_client.client_id,
            staff_user_id=test_client.staff_id,
            profession_type='medical_doctor',
            target_date = target_datetime.date(),
            target_date_utc = target_datetime.date(),
            booking_window_id_start_time = booking_start_idx,
            booking_window_id_end_time = booking_end_idx,
            booking_window_id_start_time_utc = booking_start_idx,
            booking_window_id_end_time_utc = booking_end_idx,
            client_location_id = 1,
            client_timezone='UTC',
            staff_timezone='UTC',
            charged=False,
            status='Accepted',
            payment_method_id = payment_method.idx,
            uid = uuid.uuid4(),
            consult_rate = 15.00
        )

        test_client.db.session.add(bk)

        test_client.db.session.flush()

        # add booking transcript
        twilio = Twilio()
        conversation_sid = twilio.create_telehealth_chatroom(bk.idx)

        test_client.db.session.commit()
        bookings.append(bk)

    yield bookings

    for bk in bookings:
        # delete chatroom, booking, and payment method
        chat_room = test_client.db.session.execute(select(TelehealthChatRooms).where(TelehealthChatRooms.booking_id == bk.idx)).scalars().one_or_none()
        
        # remove transcript from mongo db
        if chat_room.transcript_object_id:
            test_client.mongo.db.telehealth_transcripts.find_one_and_delete({"_id": ObjectId(chat_room.transcript_object_id)})

        for status in bk.status_history:
            test_client.db.session.delete(status)
            
        test_client.db.session.delete(chat_room)

        if bk.booking_details:
            test_client.db.session.delete(bk.booking_details)

        test_client.db.session.delete(bk)
        test_client.db.session.flush()
        
        test_client.db.session.commit()

        try:
            twilio.delete_conversation(conversation_sid)
        except TwilioRestException:
            # conversation was already removed as part of a test
            pass
