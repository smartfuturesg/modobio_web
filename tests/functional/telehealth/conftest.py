import pytest

from odyssey.api.user.models import User, UserLogin
from odyssey.api.staff.models import StaffRoles
from odyssey.utils.constants import ACCESS_ROLES

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
        consult_rate = 100
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

    pytest.telehealth_staff_created = True
    return staffs
