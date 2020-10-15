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

def clean_db(db):
    for table in reversed(db.metadata.sorted_tables):
        try:
            db.session.execute(table.delete())
        except:
            pass
    # specifically cascade drop clientinfo table
    try:
        db.session.execute('DROP TABLE "ClientInfo" CASCADE;')
    except:
        pass
    db.session.commit()
    db.drop_all()

@pytest.fixture(scope='session')
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

@pytest.fixture(scope='session')
def init_database():
    clean_db(db)
    # Create the database and the database table
    db.create_all()

    # run .sql file to create db procedures
    #  read client_data_storage_file, remove comments,
    #  execute, raw sql on database
    with open ("database/client_data_storage.sql", "r") as f:
        data=f.readlines()

    dat = [x for x in data if not x.startswith('--')]
    
    db.session.execute(''.join(dat))

    with open ("database/addResultTypes.sql", "r") as f:
        data=f.readlines()

    db.session.execute(''.join(data))

    # Insert test client data
    client_1 = ClientInfo(**test_client_info)
    db.session.add(client_1)
    db.session.flush()

    rli = {'record_locator_id': ClientInfo().generate_record_locator_id(
        firstname = client_1.firstname, 
        lastname = client_1.lastname, 
        clientid =client_1.clientid)}

    client_1.update(rli)
    
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
