
from odyssey.api.user.models import User

def test_new_client(test_client, init_database, staff_auth_header):
    """
    GIVEN a ClientInfo model
    WHEN a new client is created
    THEN check the model attributes and functionality
    """
    new_client = User.query.filter_by(is_client = True, user_id = 1).first()
    assert new_client.email == 'test_remote_registration@gmail.com'
    assert new_client.user_id == 1