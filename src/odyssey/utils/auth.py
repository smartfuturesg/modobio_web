from base64 import b64decode
import jwt

from flask import current_app, request, make_response, g
from functools import wraps
from werkzeug.datastructures import Authorization
from werkzeug.security import safe_str_cmp, check_password_hash

from odyssey import db
from odyssey.utils.constants import ACCESS_ROLES, USER_TYPES
from odyssey.utils.errors import LoginNotAuthorized, StaffNotFound
from odyssey.api.staff.models import StaffRoles
from odyssey.api.user.models import User, UserLogin

class BasicAuth(object):
    ''' BasicAuth class is the main authentication class for 
        the ModoBio project. It's primary function is to do basic
        authentications. '''
    def __init__(self, scheme=None, header=None):
        self.scheme = scheme
        self.header = header

    def login_required(self, f=None, user_type=('staff',), staff_role=None):
        ''' The login_required method is the main method that we will be using
            for authenticating both tokens and basic authorizations.
            This method decorates each CRUD request and verifies the person
            making the request has the appropriate credentials
            
            user_type, and staff_role are expected to be lists. 

            NOTE: Some methods have overrides depending if it is a 
                  OdyBasicAuth or OdyTokenAuth object
        
                  get_auth()
                  authenticate(auth,pass)
        '''
        # Validate each entry
        if user_type is not None:
            # Check if user type is a list:
            if type(user_type) is not tuple:
                raise ValueError('user_type must be a tuple.')
            else:
                # Validate 
                self.validate_roles(user_type, USER_TYPES)
         
        if staff_role is not None:
            # Check if staff role is a list:
            if type(staff_role) is not tuple:
                raise ValueError('staff_role must be a tuple.')   
            else:
                # Validate 
                self.validate_roles(staff_role, ACCESS_ROLES)                              

        def login_required_internal(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                auth = self.get_auth()
                # Flask normally handles OPTIONS requests on its own, but in
                # the case it is configured to forward those to the
                # application, we need to ignore authentication headers and
                # let the request through to avoid unwanted interactions with
                # CORS.
                user, user_login, user_context = self.authenticate(auth, user_type)

                if user in (False, None):
                    raise LoginNotAuthorized()
                if user_type:
                    # If user_type exists (Staff or Client, etc)
                    # Check user and role access
                    self.user_role_check(user,user_type=user_type, staff_roles=staff_role)                   
                
                g.flask_httpauth_user = (user, user_login) if user else (None,None)
                return f(*args, **kwargs)
            return decorated
        
        if f:
            return login_required_internal(f)
        return login_required_internal
   
    def user_role_check(self, user, user_type, staff_roles=None):
        ''' user_role_check is to determine if the user accessing the API
            is a Staff member or Client '''
        # Check if logged-in user is authorized by type (staff,client)
        # then ensure the logged_in user has role

        # TODO: little bug here where we dont know which context the user is CURRENTLY logged in as
        # when we switch to JWTs, this will be part of the token payload. Which resolves this bug
        if ('staff' in user_type or 'staff_self' in user_type) and user.is_staff:
            if staff_roles:
                self.staff_access_check(user, user_type, staff_roles=staff_roles)
            else:
                return
        elif 'client' in user_type and user.is_client:
            self.client_access_check(user)
        else:
            raise LoginNotAuthorized()

    def client_access_check(self, user):
        """
        Clients should only be able to access their own content
        this check is in place to ensure that the user_id in the URI 
        is the same as the logged in user's user_id
        """

        requested_user_id = request.view_args.get('user_id')

        if requested_user_id:
            if int(requested_user_id) != user.user_id:
                raise LoginNotAuthorized()

    def staff_access_check(self, user, user_type,  staff_roles=None):
        ''' 
        staff_access_check method will be used to determine if a Staff
        member has the correct role to access the API 
        Checks to see that staff memner is accessing their own resources
        if 'staff_self' is in the user_type
        '''
        # If roles are included, now do role checks
        # If no roles were going, then all Staff has access
        # If roles were given, check if Staff member has that role
        
        # bring up the soles for the staff member
        staff_user_roles = db.session.query(StaffRoles.role).filter(StaffRoles.user_id==user_id).all()
        staff_user_roles = [x[0] for x in staff_roles]
        
        if 'staff_self' in user_type:
            if request.view_args.get('user_id') != user.user_id:
                raise LoginNotAuthorized
        if staff_roles is None or any(role in staff_user_roles for role in staff_roles):
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

    def verify_password(self, username, password):
        """ This method is used as a decorator and to store 
            the basic authorization password check
            that is defined in auth.py """
    
        user = User.query.filter_by(email=username.lower()).one_or_none()
        # if staff member is not found in db, raise error
        if not user:
            raise LoginNotAuthorized
            
        user_login  = UserLogin.query.filter_by(user_id = user.user_id).one_or_none()
            
        # make sure staff login details exist, check password
        if not user_login:
            raise LoginNotAuthorized
        elif check_password_hash(user_login.password, password):
            return user, user_login, 'basic_auth'
        else:
            raise LoginNotAuthorized         

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
        return self.verify_password(username, password)
            
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
        
        # decode and validate token 
        secret = current_app.config['SECRET_KEY']
        try:
            decoded_token = jwt.decode(token, secret, algorithms='HS256')
        except jwt.ExpiredSignatureError:
            raise LoginNotAuthorized
        
        query = db.session.query(
                            User, UserLogin
                        ).filter(
                            User.user_id==decoded_token['uid']
                        ).filter(
                            UserLogin.user_id == decoded_token['uid']
                        ).one_or_none()
                        
        return query[0], query[1], decoded_token.get('utype') 

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