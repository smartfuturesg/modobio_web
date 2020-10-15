from flask import request, make_response, g
from functools import wraps
from werkzeug.datastructures import Authorization
from werkzeug.security import safe_str_cmp
from base64 import b64decode

class OdyAuth(object):
    def __init__(self, scheme=None, realm=None, header=None):
        self.scheme = scheme
        self.realm = realm or "Authentication Required"
        self.header = header
        self.get_password_callback = None
        self.get_user_roles_callback = None
        self.auth_error_callback = None

        def default_get_password(username):
            return None

        def default_auth_error(status):
            return "Unauthorized Access", status

        self.get_password(default_get_password)
        self.error_handler(default_auth_error)

    def get_password(self, f):
        self.get_password_callback = f
        return f

    def error_handler(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            res = f(*args, **kwargs)
            res = make_response(res)
            if res.status_code == 200:
                # if user didn't set status code, use 401
                res.status_code = 401
            if 'WWW-Authenticate' not in res.headers.keys():
                res.headers['WWW-Authenticate'] = self.authenticate_header()
            return res
        self.auth_error_callback = decorated
        return decorated

    def authenticate_header(self):
        return '{0} realm="{1}"'.format(self.scheme, self.realm)

    def get_auth_password(self, auth):
        password = None
        if auth and auth.username:
            password = self.get_password_callback(auth.username)
        return password

    def role_check(self, user, roles):
        if any(role in user.access_roles for role in roles):
            return None
        else:
            return 403

    def login_required(self, f=None, role=None, optional=None):
        if f is not None and \
                (role is not None or optional is not None):  # pragma: no cover
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
                
                password = self.get_auth_password(auth)
                
                status = None
                user = self.authenticate(auth, password)
                
                if user in (False, None):
                    status = 401
                
                # if role:
                #     status = self.role_check(user, role)
                
                if not optional and status:
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

    def authenticate(self, auth, stored_password):
        if auth:
            username = auth.username
            client_password = auth.password
        else:
            username = ""
            client_password = ""
        if self.verify_password_callback:
            return self.verify_password_callback(username, client_password)
        if not auth:
            return
        return auth.username if client_password is not None and \
            stored_password is not None and \
            safe_str_cmp(client_password, stored_password) else None  

    def username(self):
        if not request.authorization:
            return ""
        return request.authorization.username

    def current_user(self):
        if hasattr(g, 'flask_httpauth_user'):
            return g.flask_httpauth_user
          
class TokenAuth(OdyAuth):
    def __init__(self, scheme='Bearer', realm=None, header=None):
        super(TokenAuth, self).__init__(scheme, realm, header)

        self.verify_token_callback = None

    def verify_token(self, f):
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
        
    def authenticate(self, auth, stored_password):
        if auth:
            token = auth['token']
        else:
            token = ""
        if self.verify_token_callback:
            return self.verify_token_callback(token)
