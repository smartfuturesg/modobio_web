import pytest

from datetime import date, timedelta

from flask.json import dumps

from odyssey.api.notifications.models import NotificationsPushRegistration
from odyssey.api.payment.models import PaymentMethods
from odyssey.api.practitioner.models import PractitionerCredentials
from odyssey.api.staff.models import StaffRoles, StaffOperationalTerritories
from odyssey.api.user.models import User, UserLogin
from odyssey.api.telehealth.models import TelehealthBookings, TelehealthBookingStatus
from odyssey.utils.constants import ACCESS_ROLES
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
            phone_number=f'911111111{i}',
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

    creds = PractitionerCredentials(
        user_id=test_client.staff_id,
        country_id=1,
        state='AZ',
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
    """ Create a telehealth booking, needed for testing. """
    tomorrow = date.today() + timedelta(days=1)

    bk = TelehealthBookings(
        client_user_id=test_client.client_id,
        staff_user_id=test_client.staff_id,
        profession_type='doctor',
        target_date=tomorrow.isoformat(),
        booking_window_id_start_time=10,
        booking_window_id_end_time=14,
        status='quo',
        client_timezone='UTC',
        staff_timezone='UTC',
        target_date_utc=tomorrow.isoformat(),
        booking_window_id_start_time_utc=10,
        booking_window_id_end_time_utc=14,
        client_location_id=1,
        payment_method_id=payment_method.idx,
        charged=False)

    test_client.db.session.add(bk)
    test_client.db.session.commit()

    yield bk

    # booking status never cleared, but contains references to booking.
    status = TelehealthBookingStatus.query.all()
    for st in status:
        test_client.db.session.delete(st)

    test_client.db.session.delete(bk)
    test_client.db.session.commit()
