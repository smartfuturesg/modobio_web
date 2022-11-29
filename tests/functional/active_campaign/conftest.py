from odyssey.integrations.active_campaign import ActiveCampaign
from odyssey.api.user.models import User, UserActiveCampaign
import pytest

@pytest.fixture(scope='module')
def create_contact(test_client):
    ac = ActiveCampaign()

    #create contact
    user =  User.query.filter_by(user_id=test_client.client_id).one_or_none()
    contact_response, list_response = ac.create_contact(user.email, user.firstname, user.lastname)
    
    yield contact_response, list_response

    # In order for tests not to depend on each other, after creating contact and running test,
    # we need to remove contact from active campaign, unless they will throw duplicate email error
    ac_contact = UserActiveCampaign.query.filter_by(user_id=test_client.client_id).one_or_none()
    ac.delete_contact(ac_contact.user_id)
