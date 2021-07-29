from odyssey.api.user.models import User

def test_new_client(test_client):
    new_client = User.query.filter_by(is_client=True, user_id=test_client.client_id).first()

    assert new_client.email == test_client.client.email
    assert new_client.user_id == test_client.client_id
