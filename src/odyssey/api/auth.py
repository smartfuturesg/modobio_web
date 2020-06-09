from flask_httpauth import HTTPBasicAuth
from odyssey.models.main import Staff
from odyssey.api.errors import error_response

# simple authentication handler allows password authentication and
# stores a current user for view functions to check against
basic_auth = HTTPBasicAuth()

@basic_auth.verify_password
def verify_password(email, password):
    """check password for API user"""
    staff_member = Staff.query.filter_by(email=lower(email)).first()
    if staff_member and staff_member.check_password(password):
        return staff_member

@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status)