
from odyssey.models.user import User, UserLogin
from tests.data import test_staff_member
from werkzeug.security import check_password_hash

def test_regular_staff_member(test_client, init_database):
    """
    GIVEN a Staff model
    WHEN a new staff is created
    THEN check the emai
    """
    user = User.query.filter_by(is_staff=True).first()
    user_login = UserLogin.query.filter_by(user_id=user.user_id).one_or_none()

<<<<<<< HEAD
    assert user.email == 'staff_member@modobio.com'
    assert user_login.check_password('password')
    assert type(user_login.get_token()) == str 
    assert user_login.check_token(user_login.get_token())
=======
    assert staff.email == 'staff_member@modobio.com'
    assert check_password_hash(staff.password, test_staff_member['password'])
    assert type(staff.get_token()) == str 
    assert staff.check_token(staff.token)
    assert staff.get_admin_role() == 'staff_admin'
>>>>>>> f6f22bdd0a4e1c5c7a056442292f0c4846a15904

    # revoke token and then check it's validity    
    user_login.revoke_token()
    assert not user_login.check_token(user_login.token)

    # make sure new tokens are different from old ones
    old_token = user_login.token
    user_login.get_token()
    assert old_token != user_login.token