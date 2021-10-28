from contextlib import contextmanager
import logging
import uuid
from bson.objectid import ObjectId
import pytest

from datetime import date, datetime, timedelta

from flask.json import dumps
from sqlalchemy import select
from twilio.base.exceptions import TwilioRestException

from odyssey.api.lookup.models import LookupBookingTimeIncrements
from odyssey.api.notifications.models import NotificationsPushRegistration
from odyssey.api.payment.models import PaymentMethods
from odyssey.api.practitioner.models import PractitionerCredentials
from odyssey.api.staff.models import StaffRoles, StaffOperationalTerritories
from odyssey.api.user.models import User, UserLogin
from odyssey.api.telehealth.models import TelehealthBookings, TelehealthBookingStatus, TelehealthChatRooms
from odyssey.integrations.twilio import Twilio
from odyssey.utils.constants import ACCESS_ROLES, TELEHEALTH_BOOKING_LEAD_TIME_HRS
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
            is_client=False,
            email_verified=True,
            modobio_id=f'ZW99TSVWP88{i}')

        test_client.db.session.add(staff)
        test_client.db.session.commit()

        staff_login = UserLogin(user_id=staff.user_id)
        staff_login.set_password('password')
        test_client.db.session.add(staff_login)
        consult_rate = 100.00
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
    """ Add staff availablity for telehealth testing. """
    role = (
        StaffRoles
        .query
        .filter_by(
            user_id=test_client.staff_id,
            role='medical_doctor')
        .one_or_none())
    
    role.consult_rate = 100.00

    creds = PractitionerCredentials(
        user_id=test_client.staff_id,
        country_id=1,
        state='FL',
        credential_type='NPI',
        credentials='good doc',
        status='verified',
        role_id=role.idx)

    test_client.db.session.add(creds)
    test_client.db.session.commit()

    yield creds

    test_client.db.session.delete(creds)
    test_client.db.session.commit()

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

    test_client.db.session.delete(role)
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

@pytest.fixture(scope='session')
def booking(test_client, payment_method):
    """ Create a telehealth booking, needed for testing.

    This bookings fixture is used in the Telehealth section of testing.
    The Twilio section has its own bookings fixture.
    """
    tomorrow = date.today() + timedelta(days=1)

    # make a telehealth booking by direct db call
    # booking is made with minimum lead time
    target_datetime = datetime.now() + timedelta(hours=TELEHEALTH_BOOKING_LEAD_TIME_HRS)
    target_datetime = target_datetime.replace(minute = 45, second=0)
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
        profession_type='doctor',
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
        external_booking_id = uuid.uuid4(),
        duration = 20
    )

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
    test_client.db.session.delete(bk)
    test_client.db.session.flush()
    
    test_client.db.session.commit()

    try:
        twilio.delete_conversation(conversation_sid)
    except TwilioRestException:
        # conversation was already removed as part of a test
        pass

