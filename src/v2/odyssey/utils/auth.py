from flask import request, make_response, g
from functools import wraps
from werkzeug.datastructures import Authorization
from werkzeug.security import safe_str_cmp, check_password_hash

from base64 import b64decode

# Objects are purely for comparison purposes
from odyssey.staff.models import Staff
from odyssey.client.models import RemoteRegistration

# Constants to compare to
from odyssey.constants import ADMIN_ROLES, USER_TYPES, STAFF_ROLES

# Import Errors
from odyssey.errors.handlers import LoginNotAuthorized

class BasicAuth(object):
    ''' BasicAuth class is the main authentication class for 
        the ModoBio project. It's primary function is to do basic
        authentications. '''
    def __init__(self, scheme=None, header=None):
        self.scheme = scheme
        self.header = header

    def login_required(self, f=None, admin_role=None, user_type=None, staff_role=None):
        ''' The login_required method is the main method that we will be using
            for authenticating both tokens and basic authorizations.
            This method decorates each CRUD request and verifies the person
            making the request has the appropriate credentials
            
            admin_role, user_type, and staff_role are expected to be lists. 

            NOTE: Some methods have overrides depending if it is a 
                  OdyBasicAuth or OdyTokenAuth object
        
                  get_auth()
                  authenticate(auth,pass)
        '''
        # Validate each entry
        if admin_role is not None:
            # Check if admin role is a list:
            if type(admin_role) is not list:
                raise ValueError('admin_role must be a list.')
            else:
                # Validate 
                self.validate_roles(admin_role, ADMIN_ROLES)

        if user_type is not None:
            # Check if user type is a list:
            if type(user_type) is not list:
                raise ValueError('user_type must be a list.')
            else:
                # Validate 
                self.validate_roles(user_type, USER_TYPES)
         
        if staff_role is not None:
            # Check if staff role is a list:
            if type(staff_role) is not list:
                raise ValueError('staff_role must be a list.')   
            else:
                # Validate 
                self.validate_roles(staff_role, STAFF_ROLES)                              

        def login_required_internal(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                auth = self.get_auth()
                # Flask normally handles OPTIONS requests on its own, but in
                # the case it is configured to forward those to the
                # application, we need to ignore authentication headers and
                # let the request through to avoid unwanted interactions with
                # CORS.
                
                user = self.authenticate(auth, user_type)
                
                if user in (False, None):
                    raise LoginNotAuthorized()
                if admin_role:
                    self.admin_check(user, admin_role)
                if user_type:
                    # If user_type exists (Staff or Client, etc)
                    # Check if they are allowed access
                    # If user_type exists, it will call role_check
                    
                    self.user_check(user, user_type, staff_roles=staff_role)
                elif staff_role:
                    self.role_check(user,staff_role)                   
                
                g.flask_httpauth_user = user if user else None
                return f(*args, **kwargs)
            return decorated
        
        if f:
            return login_required_internal(f)
        return login_required_internal

    def admin_check(self, user, admin_role):
        ''' Role suppression
        sys_admin: permisison to create staff admin.
        staff_admin:  can create all other roles except staff/systemadmin
        '''
        if len(admin_role) == 1:
            # if sys_admin is in the login requirement, check if user has that access
            if 'sys_admin' in admin_role:
                if not user.is_system_admin:
                    raise LoginNotAuthorized
            # if staff_admin is in the login requirement, check if user has that access
            if 'staff_admin' in admin_role:
                if not user.is_admin:
                    raise LoginNotAuthorized
        else:
            if user.is_system_admin or user.is_admin:
                return None
            else:
                raise LoginNotAuthorized
        return None 

    def user_check(self, user, user_type, staff_roles=None):
        ''' user_check is to determine if the user accessing the API
            is a Staff member or Client '''
        # First check the user type. If the user_type is wrong, then
        # the user absolutely has no access

        if len(user_type) == 2:
            if not isinstance(user,(Staff,RemoteRegistration)):
                # User is NEITHER Staff nor RemoteRegistration
                raise LoginNotAuthorized
        else:
            if 'staff' in user_type:
                if not isinstance(user,Staff):
                    raise LoginNotAuthorized
                else:
                    # USER IS STAFF
                    return self.role_check(user,staff_roles)
            
            elif 'remoteregistration' in user_type:
                if not isinstance(user,RemoteRegistration):
                    raise LoginNotAuthorized
                else:
                    # USER IS CLIENT
                    # Now, check if the api requires a clientid, and if it does,
                    # the Current Client can ONLY see their own information
                    if 'clientid' in request.args:
                        # If the request parameter contains clientid,
                        # check if the user's client id matches the parameter id
                        # if they are NOT equal, return 411
                        if user.clientid != request.args.get('clientid'):
                            raise LoginNotAuthorized
        return

    def role_check(self, user, staff_roles=None):
        ''' role_check method will be used to determine if a Staff
            member has the correct role to access the API '''
        # If roles are included, now do role checks
        # If no roles were going, then all Staff has access
        # If roles were given, check if Staff member has that role
        if staff_roles is None or any(role in user.access_roles for role in staff_roles):
            # Staff member's role matches the Role Requirement in the API
            return None
        else:
            raise LoginNotAuthorized

    def validate_roles(self, roles, constants):
        # Validate 
        for role in roles:
            if role not in constants:
                ValueError('{} is not in {}'.format(role, constants))
        return 

    def verify_password(self, user_type, username, password):
        ''' This method is used as a decorator and to store 
            the basic authorization password check
            that is defined in auth.py '''
        
        if 'staff' in user_type:
            """check password for API user"""
            staff_member = Staff.query.filter_by(email=username.lower()).one_or_none()
            if staff_member and check_password_hash(staff_member.password, password):
                return staff_member
        elif 'remoteregistration' in user_type:
            """check password for at-home client"""
            client = RemoteRegistration.query.filter_by(
                        email=username.lower()).order_by(
                        RemoteRegistration.registration_portal_expiration.desc()).first()
            if client and password == client.password:
                return client            

    def get_auth(self):
        ''' This method is to authorize basic connections '''
        # this version of the Authorization header parser is more flexible
        # than Werkzeug's, as it also accepts other schemes besides "Basic"
        header = self.header or 'Authorization'
        if header not in request.headers:
            return None
        value = request.headers[header].encode('utf-8')
        try:
            scheme, credentials = value.split(b' ', 1)
            username, password = b64decode(credentials).split(b':', 1)
        except (ValueError, TypeError):
            return None
        return Authorization(
            scheme, {'username': username.decode('utf-8'),
                     'password': password.decode('utf-8')})

    def authenticate(self, auth, user_type):
        ''' authenticate method will use the verify_password_callback method
            to return the person's basic authentication. '''
        if auth:
            username = auth.username
            password = auth.password
        else:
            username = ""
            password = ""
        return self.verify_password(user_type, username, password)
            
    def current_user(self):
        ''' current_user method returns the current instance 
            user, flask_httpauth_user, if it exists. '''
        if hasattr(g, 'flask_httpauth_user'):
            return g.flask_httpauth_user
          
class TokenAuth(BasicAuth):
    ''' TokenAuth class extends the OdyBasicAuth class. 
        It's primary function is to do token authentications. '''    
    def __init__(self, scheme='Bearer', header=None):
        super(TokenAuth, self).__init__(scheme, header)

        self.verify_token_callback = None

    def verify_token(self, user_type, token):
        ''' verify_token is a method that is used as a decorator to store 
            the token checking process that is defined in auth.py '''
        
        # TODO REMOVE THIS
        if user_type is None:
            user_type = ['staff']

        if 'staff' in user_type:
            return Staff.check_token(token) if token else None
        elif 'remoteregistration' in user_type:
            return RemoteRegistration.check_token(token) if token else None

    def get_auth(self):
        ''' This method is to authorize tokens '''
        auth = None
        if self.header is None or self.header == 'Authorization':
            auth = request.authorization
            if auth is None and 'Authorization' in request.headers:
                # Flask/Werkzeug do not recognize any authentication types
                # other than Basic or Digest, so here we parse the header by
                # hand
                try:
                    auth_type, token = request.headers['Authorization'].split(
                        None, 1)
                    auth = Authorization(auth_type, {'token': token})
                except (ValueError, KeyError):
                    # The Authorization header is either empty or has no token
                    pass
        elif self.header in request.headers:
            # using a custom header, so the entire value of the header is
            # assumed to be a token
            auth = Authorization(self.scheme,
                                 {'token': request.headers[self.header]})

        # if the auth type does not match, we act as if there is no auth
        # this is better than failing directly, as it allows the callback
        # to handle special cases, like supporting multiple auth types
        if auth is not None and auth.type.lower() != self.scheme.lower():
            auth = None

        return auth
        
    def authenticate(self, auth, user_type):
        ''' This authenticate method overrides the authenticate method in 
            the OdyBasicAuth authenticate method and returns an object defined
            in verify_token_callback'''
        if auth:
            token = auth['token']
        else:
            token = ""
        return self.verify_token(user_type, token)

# simple authentication handler allows password authentication and
# stores a current user for view functions to check against
basic_auth = BasicAuth()
token_auth = TokenAuth()