from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from odyssey.models.staff import Staff
from odyssey.models.user import User
from odyssey.models.client import RemoteRegistration
from odyssey.api.errors import error_response

# simple authentication handler allows password authentication and
# stores a current user for view functions to check against
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

basic_auth_client = HTTPBasicAuth()
token_auth_client = HTTPTokenAuth()

@basic_auth_client.verify_password
def verify_password_client(email, password):
    """check password for at-home client"""
    #take the most recent entry
    client = RemoteRegistration.query.filter_by(
                email=email.lower()).order_by(
                RemoteRegistration.registration_portal_expiration.desc()).first()
    if client and client.check_password(password):
        return client

@token_auth_client.verify_token
def verify_token_client(token):
    return RemoteRegistration.check_token(token) if token else None
    
@basic_auth.verify_password
def verify_password(email, password):
    """check password for API user"""
    user = User.query.filter_by(email=email.lower()).first()
    if user and user.check_password(password):
        return user

@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status)

@token_auth.verify_token
def verify_token(token):
    return User.check_token(token) if token else None

@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)

@token_auth.get_user_roles
def get_user_roles(user):
    return user.get_admin_role()