from odyssey.api.user.models import User, UserLogin
from werkzeug.security import check_password_hash

def test_regular_staff_member(test_client):
    breakpoint()
    user = User.query.filter_by(email=test_client.staff.email).first()
    user_login = UserLogin.query.filter_by(user_id=test_client.staff_id).one_or_none()
    assert user.is_staff == True
    assert check_password_hash(user_login.password, test_client.staff_pass)
