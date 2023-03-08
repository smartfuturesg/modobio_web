from odyssey.integrations.active_campaign import ActiveCampaign
from odyssey.api.user.models import User, UserActiveCampaign
import pytest
import random
import string

@pytest.fixture(scope='module')
def create_client_contact(test_client):
    ac = ActiveCampaign()

    #create contact
    user =  User.query.filter_by(user_id=test_client.client_id).one_or_none()

    
    #Give user temporary email with random characters to avoid potential conflicts in AC
    random_chars = ''.join(random.choice(string.ascii_lowercase) for _ in range(7))
    user_email = f'{random_chars}.{user.email}'
    user.email = user_email
    test_client.db.session.commit()

    #Create contact in active campaign
    contact_response, list_response = ac.create_contact(user_email, user.firstname, user.lastname)
    
    yield contact_response, list_response

    # In order for tests not to depend on each other, after creating contact and running test,
    # we need to remove contact from active campaign, unless they will throw duplicate email error
    ac_contact = UserActiveCampaign.query.filter_by(user_id=test_client.client_id).one_or_none()
    ac.delete_contact(ac_contact.user_id)

@pytest.fixture(scope='module')
def create_provider_contact(test_client):
    ac = ActiveCampaign()

    #create contact
    user =  User.query.filter_by(user_id=test_client.provider_id).one_or_none()
    
    #Give user temporary email with random characters to avoid potential conflicts
    random_chars = ''.join(random.choice(string.ascii_lowercase) for _ in range(7))
    user_email = f'{random_chars}.{user.email}'
    user.email = user_email
    test_client.db.session.commit()

    #Create contact in active campaign
    contact_response, list_response = ac.create_contact(user_email, user.firstname, user.lastname)
    
    yield contact_response, list_response

    # In order for tests not to depend on each other, after creating contact and running test,
    # we need to remove contact from active campaign, unless they will throw duplicate email error
    ac_contact = UserActiveCampaign.query.filter_by(user_id=test_client.provider_id).one_or_none()
    ac.delete_contact(ac_contact.user_id)
