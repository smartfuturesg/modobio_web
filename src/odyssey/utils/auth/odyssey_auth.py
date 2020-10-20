from flask import request, make_response, g
from functools import wraps
from werkzeug.datastructures import Authorization
from werkzeug.security import safe_str_cmp
from base64 import b64decode

class OdyBasicAuth(object):
    ''' OdyBasicAuth class is the main authentication class for 
        the ModoBio project. It's primary function is to do basic
        authentications. '''
    def __init__(self, scheme=None, realm=None, header=None):
        self.scheme = scheme
        self.realm = realm or "Authentication Required"
        self.header = header
        self.auth_error_callback = None

        def default_auth_error(status):
            return "Unauthorized Access", status
        
        self.error_handler(default_auth_error)

    def error_handler(self, f):
        ''' Error handler for OdyBasicAuth class. '''
        @wraps(f)
        def decorated(*args, **kwargs):
            res = f(*args, **kwargs)
            res = make_response(res)
            if res.status_code == 200:
                # if user didn't set status code, use 401
                res.status_code = 401
            if 'WWW-Authenticate' not in res.headers:
                res.headers['WWW-Authenticate'] = self.authenticate_header()
            return res
        self.auth_error_callback = decorated
        return decorated

    def authenticate_header(self):
        ''' authenticate header '''
        return '{0} realm="{1}"'.format(self.scheme, self.realm)

    def role_check(self, user, roles):
        ''' role_check method will be used for future cases to check
            the user's roles '''
        if any(role in user.access_roles for role in roles):
            return None
        else:
            return 403

    def login_required(self, f=None, role=None):
        ''' The login_required method is the main method that we will be using
            for authenticating both tokens and basic authorizations.
            This method decorates each CRUD request and verifies the person
            making the request has the appropriate credentials
            
            NOTE: Some methods have overrides depending if it is a 
                  OdyBasicAuth or OdyTokenAuth object
        
                  get_auth()
                  authenticate(auth,pass)
             '''
        if f is not None and \
                (role is not None):  # pragma: no cover
            raise ValueError(
                'role and optional are the only supported arguments')
        def login_required_internal(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                
                auth = self.get_auth()
                # Flask normally handles OPTIONS requests on its own, but in
                # the case it is configured to forward those to the
                # application, we need to ignore authentication headers and
                # let the request through to avoid unwanted interactions with
                # CORS.
                    
                status = None
                user = self.authenticate(auth)
                if user in (False, None):
                    status = 401
                
                # if role:
                #     status = self.role_check(user, role)
                
                if status:
                    # Clear TCP receive buffer of any pending data
                    request.data
                    try:
                        return self.auth_error_callback(status)
                    except TypeError:
                        return self.auth_error_callback()
                
                g.flask_httpauth_user = user if user is not True \
                    else auth.username if auth else None
                return f(*args, **kwargs)
            return decorated
        
        if f:
            return login_required_internal(f)
        return login_required_internal

    def verify_password(self, f):
        ''' This method is used as a decorator and to store 
            the basic authorization password check
            that is defined in auth.py '''
        self.verify_password_callback = f
        return f

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

    def authenticate(self, auth):
        ''' authenticate method will use the verify_password_callback method
            to return the person's basic authentication. '''
        if auth:
            username = auth.username
            client_password = auth.password
        else:
            username = ""
            client_password = ""
        if self.verify_password_callback:
            return self.verify_password_callback(username, client_password)

    def current_user(self):
        ''' current_user method returns the current instance 
            user, flask_httpauth_user, if it exists. '''
        if hasattr(g, 'flask_httpauth_user'):
            return g.flask_httpauth_user
          
class OdyTokenAuth(OdyBasicAuth):
    ''' OdyTokenAuth class extends the OdyBasicAuth class. 
        It's primary function is to do token authentications. '''    
    def __init__(self, scheme='Bearer', realm=None, header=None):
        super(OdyTokenAuth, self).__init__(scheme, realm, header)

        self.verify_token_callback = None

    def verify_token(self, f):
        ''' verify_token is a method that is used as a decorator to store 
            the token checking process that is defined in auth.py '''
        self.verify_token_callback = f
        return f

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
        
    def authenticate(self, auth):
        ''' This authenticate method overrides the authenticate method in 
            the OdyBasicAuth authenticate method and returns an object defined
            in verify_token_callback'''
        if auth:
            token = auth['token']
        else:
            token = ""
        if self.verify_token_callback:
            return self.verify_token_callback(token)
