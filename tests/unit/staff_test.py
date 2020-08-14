
from odyssey.models.staff import Staff
from tests.data import test_staff_member

def test_regular_staff_member(test_client, init_database):
    """
    GIVEN a Staff model
    WHEN a new staff is created
    THEN check the emai
    """
    staff = Staff().query.first()

    assert staff.email == 'staff_member@modobio.com'
    assert staff.check_password(test_staff_member['password'])
    assert type(staff.get_token()) == str 
    assert staff.check_token(staff.token)
    assert staff.get_admin_role() == 'staff_admin'

    # revoke token and then check it's validity    
    staff.revoke_token()
    assert not staff.check_token(staff.token)

    # make sure new tokens are different from old ones
    old_token = staff.token
    staff.get_token()
    assert old_token != staff.token
