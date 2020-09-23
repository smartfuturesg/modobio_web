
from odyssey.models.client import ClientInfo

def test_new_client(test_client, init_database):
    """
    GIVEN a ClientInfo model
    WHEN a new client is created
    THEN check the model attributes and functionality
    """
    new_client = ClientInfo().query.first()
    assert new_client.email == 'test_this_client@gmail.com'
    assert new_client.record_locator_id == 'TC148FAC4'
    assert new_client.clientid == 1