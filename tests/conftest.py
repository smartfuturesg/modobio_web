from odyssey import create_app, db
from odyssey.models.intake import ClientInfo
from odyssey.models.main import Staff
import pytest 

from .data import test_client_info, test_staff_member

@pytest.fixture(scope='module')
def new_client():
    """
        create a test client using the client info table
    """
    client = ClientInfo()
    client.from_dict(test_client_info)
    return client

@pytest.fixture(scope='module')
def test_client():
    """flask application instance (client)"""
    app = create_app(flask_env='testing')
    testing_client = app.test_client()
    
    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()
    
    yield testing_client

    ctx.pop()

@pytest.fixture(scope='module')
def init_database():
    # Create the database and the database table
    db.create_all()

    # Insert test client data
    client_1 = ClientInfo()
    client_1.from_dict(test_client_info)
    db.session.add(client_1)

    # initialize a test staff member
    staff_1 = Staff()
    staff_1.from_dict(test_staff_member)
    staff_1.set_password(test_staff_member['password'])
    db.session.add(staff_1)

    # Commit the changes for the users
    db.session.commit()

    yield db  # this is where the testing happens!

    db.drop_all()
