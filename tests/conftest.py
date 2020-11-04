import os
import pytest
from datetime import datetime
from sqlalchemy import text

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
from odyssey.models.user import User, UserLogin

from .data import (
    test_new_client_creation,
    test_new_client_info,
    test_new_client_login,
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

    # run .sql files to create db procedures and initialize 
    # some tables
    #  read .sql files, remove comments,
    #  execute, raw sql on database
    sql_scripts = ['database/'+f for f in os.listdir('database/') if f.endswith(".sql")]
    for sql_script in sql_scripts:
        with open (sql_script, "r") as f:
            data=f.readlines()

        dat = [x for x in data if not x.startswith('--')]
    
        db.session.execute(text(''.join(dat)))

    # Insert test client data
    client_1 = User(**test_new_client_creation)
    db.session.add(client_1)
    db.session.flush()
    client_1_login = UserLogin(**{'user_id': client_1.user_id})
    test_new_client_info['user_id'] = client_1.user_id
    client_1_info = ClientInfo(**test_new_client_info)
    db.session.add(client_1_login)
    db.session.add(client_1_info)
    db.session.flush()

    rli = {'record_locator_id': ClientInfo().generate_record_locator_id(
        firstname = client_1.firstname, 
        lastname = client_1.lastname, 
        user_id =client_1.user_id)}

    client_1_info = ClientInfo.query.filter_by(user_id=client_1.user_id)
    client_1.update(rli)
    
    # initialize a test staff member
    staff_1 = User(**test_staff_member)
    db.session.add(staff_1)
    db.session.flush()
    staff_1_login = UserLogin(**{"user_id": staff_1.user_id})
    staff_1_login.set_password('password')
    db.session.add(staff_1_login)

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