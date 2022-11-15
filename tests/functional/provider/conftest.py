from json import dumps
import pytest

from tests.utils import login

from odyssey.api.user.models import User, UserLogin

@pytest.fixture(scope='function')
def client_user(test_client):
    """
    Generates a new client user 
    """
    user_data = {
        "firstname": "Test",
        "email": "tmp_test_client@tester.com",
        "middlename": "middlename",
        "lastname": "lastname",
        "password": "123",
    } 

    response = test_client.post(
        '/user/client/',
        data=dumps(user_data),
        content_type='application/json')

    user = User.query.filter_by(email=user_data['email']).first()
    auth_header = login(test_client, user, password=user_data['password'])

    # verify email
    response = test_client.post(
        f'/user/email-verification/code/{response.json["user_info"]["user_id"]}/?code={response.json.get("email_verification_code")}',
        headers = auth_header,
        content_type='application/json'
        )

    yield {"user":user, "auth_header": auth_header}

    # delete UserLogin and User
    UserLogin.query.filter_by(user_id=user.user_id).delete()
    User.query.filter_by(user_id=user.user_id).delete()
    
    test_client.db.session.commit()

        