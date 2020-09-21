import pytest

from odyssey import create_app, db
from odyssey.models.client import (
    ClientInfo,
    ClientConsent,
    ClientRelease,
    ClientPolicies,
    ClientConsultContract,
    ClientSubscriptionContract,
    ClientIndividualContract
)
from odyssey.models.misc import MedicalInstitutions

from odyssey.models.staff import Staff

from .data import (
    test_client_info,
    test_staff_member,
    test_client_consent_data,
    test_client_release_data,
    test_client_policies_data,
    test_client_consult_data,
    test_client_subscription_data,
    test_client_individual_data
)

<<<<<<< HEAD
=======
# from odyssey.utils.schemas import ClientInfoSchema

>>>>>>> 7bbe713294afcaa70295f9af3ccf8fb2eb3dd765
def clean_db(db):
    for table in reversed(db.metadata.sorted_tables):
        try:
            db.session.execute(table.delete())
        except:
            pass
    db.session.commit()
    db.drop_all()

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
    app = create_app()
    db.init_app(app)
    testing_client = app.test_client()
    
    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()
    
    yield testing_client

    ctx.pop()

@pytest.fixture(scope='module')
def init_database():
    clean_db(db)
    # Create the database and the database table
    db.create_all()

    # Insert test client data
    client_1 = ClientInfo(**test_client_info)

    db.session.add(client_1)
    db.session.commit()

    clientid = client_1.clientid

    # initialize a test staff member
    staff_1 = Staff(**test_staff_member)
    staff_1.set_password(test_staff_member['password'])
    db.session.add(staff_1)

    #initialize Medical institutes table
    med_institute1 = MedicalInstitutions(institute_name='Mercy Gilbert Medical Center')
    med_institute2 = MedicalInstitutions(institute_name='Mercy Tempe Medical Center')

    db.session.add_all([med_institute1, med_institute2])

    # Commit the changes for the users
    db.session.commit()

    yield db  # this is where the testing happens!
    clean_db(db)

    # https://stackoverflow.com/questions/26350911/what-to-do-when-a-py-test-hangs-silently
    db.session.close()
