
from odyssey.models.user import User, UserLogin
from tests.data import test_staff_member

def test_regular_staff_member(test_client, init_database):
    """
    GIVEN a Staff model
    WHEN a new staff is created
    THEN check the emai
    """
    user = User.query.filter_by(is_staff=True).first()
    user_login = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()

    assert user.email == 'staff_member@modobio.com'
    assert user_login.check_password(test_staff_member['password'])
    assert type(user_login.get_token()) == str 
    assert user_login.check_token(user.token)

    # revoke token and then check it's validity    
    user_login.revoke_token()
    assert not user_login.check_token(user.token)

    # make sure new tokens are different from old ones
    old_token = user_login.token
    user_login.get_token()
    assert old_token != user_login.token