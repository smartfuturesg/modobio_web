
from odyssey.models.staff import Staff
from tests.data import test_staff_member

def test_regular_staff_member(test_client, init_database):
    """
    GIVEN a Staff model
    WHEN a new staff is created
    THEN check the emai
    """
    staff = Staff().query.first()
    user = User.query.filter_by(user_id=staff.user_id)

    assert staff.email == 'staff_member@modobio.com'
    assert staff.check_password(test_staff_member['password'])
    assert type(user.get_token()) == str 
    assert user.check_token(user.token)

    # revoke token and then check it's validity    
    user.revoke_token()
    assert not user.check_token(user.token)

    # make sure new tokens are different from old ones
    old_token = user.token
    user.get_token()
    assert old_token != user.token
