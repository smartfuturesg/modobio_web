import pytest

from odyssey import create_app, db
from odyssey.models.intake import (
    ClientInfo,
    ClientConsent,
    ClientRelease,
    ClientPolicies,
    ClientConsultContract,
    ClientSubscriptionContract,
    ClientIndividualContract
)

from odyssey.models.main import Staff

from .data import (
    test_client_info,
    test_staff_member,
    test_client_consent_form,
    test_client_release_form,
    test_client_policies_form,
    test_client_consult_contract,
    test_client_subscription_contract,
    test_client_individual_contract
)

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
    db.session.commit()
    clientid = client_1.clientid

    # initialize a test staff member
    staff_1 = Staff()
    staff_1.from_dict(test_staff_member)
    staff_1.set_password(test_staff_member['password'])
    db.session.add(staff_1)

    # Populate document tables
    consent_1 = ClientConsent(clientid=clientid, **test_client_consent_form)
    db.session.add(consent_1)

    release_1 = ClientRelease(clientid=clientid, **test_client_release_form)
    db.session.add(consent_1)

    policies_1 = ClientPolicies(clientid=clientid, **test_client_policies_form)
    db.session.add(policies_1)

    consult_1 = ClientConsultContract(clientid=clientid, **test_client_consult_contract)
    db.session.add(consult_1)

    subscription_1 = ClientSubscriptionContract(clientid=clientid, **test_client_subscription_contract)
    db.session.add(subscription_1)

    individual_1 = ClientIndividualContract(clientid=clientid, **test_client_individual_contract)
    db.session.add(individual_1)

    # Commit the changes for the users
    db.session.commit()

    yield db  # this is where the testing happens!

    db.drop_all()
