from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from odyssey.models.user import User, UserLogin
from odyssey.api.errors import error_response

# simple authentication handler allows password authentication and
# stores a current user for view functions to check against
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(email, password):
    """check password for API user"""
    user = User.query.filter_by(email=email.lower()).first()
    if user:
        user_login = UserLogin.query.filter_by(user_id=user.user_id).one_or_none()
        if user_login.check_password(password):
            return user

@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status)

@token_auth.verify_token
def verify_token(token):
    return UserLogin.check_token(token) if token else None

@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)