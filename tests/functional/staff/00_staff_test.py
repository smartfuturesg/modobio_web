from odyssey.api.user.models import User, UserLogin
from werkzeug.security import check_password_hash

def test_regular_staff_member(test_client, init_database, staff_auth_header):
    """
    GIVEN a Staff model
    WHEN a new staff is created
    THEN check the email
    """
    user = User.query.filter_by(is_staff=True).first()
    user_login = UserLogin.query.filter_by(user_id=user.user_id).one_or_none()
    assert user.email == 'new_staff_1@modo.com'
    #assert check_password_hash(user_login.password, 'password')