import logging
logger = logging.getLogger(__name__)

from base64 import b64decode
import jwt

from flask import current_app, request, g
from functools import wraps
from sqlalchemy import select
from werkzeug.datastructures import Authorization
from werkzeug.exceptions import Unauthorized, BadRequest
from werkzeug.security import check_password_hash

from odyssey import db
from odyssey.api.client.models import ClientClinicalCareTeamAuthorizations
from odyssey.api.lookup.models import LookupClinicalCareTeamResources
from odyssey.utils.constants import ACCESS_ROLES, DB_SERVER_TIME, PROVIDER_ROLES, STAFF_ROLES, USER_TYPES
from odyssey.api.staff.models import StaffRoles
from odyssey.api.user.models import User, UserLogin, UserTokenHistory

class BasicAuth(object):
    ''' BasicAuth class is the main authentication class for 
        the ModoBio project. It's primary function is to do basic
        authentications. '''
    def __init__(self, scheme=None, header=None):
        self.scheme = scheme
        self.header = header

    def login_required(self, f=None, user_type=('staff','client', 'provider'), staff_role=None, email_required=True, resources = ()):
        ''' The login_required method is the main method that we will be using
            for authenticating both tokens and basic authorizations.
            This method decorates each CRUD request and verifies the person
            making the request has the appropriate credentials
            
            user_type, and staff_role are expected to be lists. 

            NOTE: Some methods have overrides depending if it is a 
                  BasicAuth or TokenAuth object
        
                  get_auth()
                  authenticate(auth,pass)
        '''
        logger.debug(f'Login required wrapper called with args: f={f}, user_type={user_type}, '
                     f'staff_role={staff_role}, '
                     f'email_required={email_required}, resources={resources}')

        ###
        ##  Validate kwargs: user_type, staff_role
        ###
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
                """
                Steps to authentication and authorization
                1. Pull auth details from headers (basic or bearer token)
                2. Authenticate credentials and bring up the user and user login details
                    -user_context either 'basic_auth' (logging in) or 
                     pulled from token: 'client' or 'staff' 
                3. Verify that user meets authorization requirements for the endpoint. These include
                    - user_type: 
                        - 'client', 
                        - 'staff' 
                        - 'staff_self' (for staff editing their own personal details)
                        - 'modobio' anyone logged in through the modobio platform
                        - 'provider'
                    - staff_role: roles specified in utils/constants
                    
                Any issues coming from the above should raise a 401 error with no message.
                """
                self.staff_role = staff_role
                self.user_type = user_type
                self.resources = resources
                
                logger.debug(f'Login required decorator called with: f={f}, user_type={user_type}, '
                             f'staff_role={staff_role}, '
                             f'email_required={email_required}, resources={resources}'
                             )
                
                auth = self.get_auth()
                
                # Authenticate and load user and user login details
                user, user_login, user_context = self.authenticate(auth)
                
                if user in (False, None):
                    raise Unauthorized

                if email_required and not user.email_verified:
                    raise BadRequest('Please verify your email address.')

                # If user_type exists (Staff or Client, etc)
                # Check user and role access
                if user_type:
                    # If user_type exists (Staff or Client, etc)
                    # Check user and role access
                    self.user_role_check(
                        user,
                        user_login,
                        user_context,)
                
                g.flask_httpauth_user = (user, user_login) if user else (None,None)
                return f(*args, **kwargs)
            return decorated
        
        if f:
            return login_required_internal(f)
        return login_required_internal
   
    def user_role_check(self, user: User, user_login: UserLogin, user_context: str):
        ''' user_role_check is to determine if the user accessing the API
            is a Staff member or Client '''
        # user is logged in as a modobio user, they may access the endpoint
        if 'modobio' in self.user_type:
            return

        # User is logged in, claims staff in token (user_context),
        # user is registered as staff member (user.is_staff),
        # and endpoint requests staff or staff_self (user_type).
        elif (user_context == 'staff' and user.is_staff and
              ('staff' in self.user_type or 'staff_self' in self.user_type)):
            # Account is blocked
            if user_login.staff_account_blocked:
                raise Unauthorized('Your staff account has been blocked. Please contact '
                                   'client_services@modobio.com to resolve the issue.')
            # Check staff roles and access.
            if self.staff_role or 'staff_self' in self.user_type or len(self.resources) > 0:
                self.staff_access_check(user)

        # User is logged in, claims client in token (user_context),
        # user is registered as client (user.is_client),
        # and endpoint requests client (user_type).
        elif user_context == 'client' and user.is_client and 'client' in self.user_type:
            # Account is blocked.
            if user_login.client_account_blocked:
                raise Unauthorized('Your client account has been blocked. Please contact '
                                   'client_services@modobio.com to resolve the issue.')
            # Check client access.
            self.client_access_check(user)

        elif (user_context == 'provider' and user.is_provider and 
            ('provider' in self.user_type or 'staff_self' in self.user_type)):
            # Account is blocked
            if user_login.staff_account_blocked:
                raise Unauthorized('Your provider account has been blocked. Please contact '
                                   'client_services@modobio.com to resolve the issue.')
            # Check staff roles, resources, and user_type.
            if self.staff_role or 'staff_self' in self.user_type or len(self.resources) > 0:
                self.provider_access_check(user)

        # User is logging in
        elif user_context == 'basic_auth':
            # /staff/token/ endpoint and user is registered staff member
            if 'staff' in self.user_type and user.is_staff:
                if user_login.staff_account_blocked:
                    raise Unauthorized('Your staff account has been blocked. Please contact '
                                       'client_services@modobio.com to resolve the issue.')
            # /client/token/ endpoint and user is registered client
            elif self.user_type == ('client',) and user.is_client:
                if user_login.client_account_blocked:
                    raise Unauthorized('Your client account has been blocked. Please contact '
                                       'client_services@modobio.com to resolve the issue.')
            # /provider/token/ endpoint and user is registered client
            elif 'provider' in self.user_type and user.is_provider:
                if user_login.staff_account_blocked:
                    raise Unauthorized('Your provider account has been blocked. Please contact '
                                       'client_services@modobio.com to resolve the issue.')
            else:
                raise Unauthorized
        else:
            raise Unauthorized

    def client_access_check(self, user):
        """
        Clients can access content in one of two scenarios:
            1. They are attempting to access their own content.
            2. Clients may access certain resources belonging to other users
                who have given authorization as part of their clinical care team.
        """

        requested_user_id = request.view_args.get('user_id', request.view_args.get('client_user_id'))

        if requested_user_id:
            # user is attempting to access their own data
            if int(requested_user_id) == user.user_id:
                return
            # client would like to see another client's data
            # through the clinical care team system
            else:
                # ensure request is GET
                if request.method != 'GET':
                    raise Unauthorized
                # resources must be specified for endpoint designated by table name
                # e.g. @token_auth.login_required(resources=('MedicalSocialHistory','MedicalSTDHistory'))
                if len(self.resources) == 0:
                    raise Unauthorized
                # set the context and successful authorizations list in the g object
                g.clinical_care_context = True
                g.clinical_care_authorized_resources = []
                # search db for this resource authorization
                for resource in self.resources:
                    is_authorized = db.session.query(
                        ClientClinicalCareTeamAuthorizations.resource_id, LookupClinicalCareTeamResources.resource_name
                    ).filter(ClientClinicalCareTeamAuthorizations.team_member_user_id == user.user_id
                    ).filter(ClientClinicalCareTeamAuthorizations.user_id == requested_user_id
                    ).filter(ClientClinicalCareTeamAuthorizations.resource_id == LookupClinicalCareTeamResources.resource_id
                    ).filter(LookupClinicalCareTeamResources.resource_name == resource
                    ).filter(ClientClinicalCareTeamAuthorizations.status == 'accepted'
                    ).all()
                    if len(is_authorized) == 1:
                        g.clinical_care_authorized_resources.append(resource)
                        continue
                if len(g.clinical_care_authorized_resources) == 0:
                    # this user does not have access to this content
                    raise Unauthorized
        return

    def staff_access_check(self, user):
        """ Check whether staff member has access rights.

        staff_access_check method will be used to determine if a Staff
        member has the correct role and user privileges to access the endpoint.

        Altogether, here are the variables involved in staff member authorization:

        - being logged in as a staff member (utype='staff' in the token payload)
        - staff_role (e.g. token_auth.login_required(staff_role=('client_services',)

        A note on staff roles:
            Internal users which do not engage with clients in any medical capacity.
            e.g. staff_admin, client_services.
            In some cases, client data may be exposed to these users. Holding one of 
            these roles gives them the privilege of viewing certain user resources 
            (both client and provider). Care team permissions do not apply to these users.  
         
    
        There are several scenarios which staff can access endpoints from:

        1.  Endpoint requires only a valid token. In which case, no further access
            checks are required this function is skipped.
        2.  Staff is trying to access their own resources.
            - user_id (or sometimes staff_user_id) will be a request argument
            - 'staff_self' will be in user_type

            Using these two pieces of info, we will just check that the logged-in
            user is the same as the user being requested in the request argument
            (user_id or staff_user_id)

        3.  Staff is accessing another user's resources. In general, we do not want staff members
            to be able to access client's resources. However, certain roles may grant access
            to client, provider, or staff account details. Currently we do not require staff members
            to be given explicit access to client data in the way we have with provider access through the
            team member system. 

            a. Only ``user_type`` is specified. Just being a staff member is enough.
            b. Roles are required (e.g. staff_admin). Staff member must meet role
                requirements as well. 
        """
        # bring up the roles for the staff member
        staff_user_roles = db.session.query(StaffRoles.role).filter(StaffRoles.user_id==user.user_id).all()
        staff_user_roles = [x[0] for x in staff_user_roles]

        requested_user_id =  request.view_args.get('user_id', request.view_args.get('client_user_id', request.view_args.get('staff_user_id')))
        
        # staff accessing their own resources
        # request args will either contain user_id or staff_user_id which must match the logged-in user
        # if logged-in staff is not the user being requested and no role requirement, raise unauthorized
        if 'staff_self' in self.user_type \
            and requested_user_id == user.user_id:
            return
        
        elif 'staff_self' in self.user_type \
            and requested_user_id not in (None, user.user_id)  \
            and self.staff_role is None:
                raise Unauthorized

        # check Staff member's roles match the role requirement in the endpoint
        elif self.staff_role is not None:
            if not any(role in staff_user_roles for role in self.staff_role):
                raise Unauthorized

        # Staff is accessing client resources without role or resource authorization
        else:
            logger.debug(f'Staff user granted access to endpoint without checks: {request.path}')
            return

        # authorization checks all end here
        return

    def provider_access_check(self, user: User):
        """ Check whether staff member has access rights.

        provider_access_check method will be used to determine if a Staff
        member has the correct role and care team privileges to access the API

        Altogether, here are the variables involved in provider member authorization:

        - being logged in as a staff member (utype='provider' in the token payload)
        - care team resources (e.g. token_auth.login_required(resources=('MedicalHistory',)))
        - staff_role (e.g. token_auth.login_required(staff_role=('medical_doctor',)
            
        There are several scenarios which providers can access endpoints from:

        1.  Endpoint requires only a valid token. In which case, no further access
            checks are required this function is skipped.
        2.  Provider is trying to access their own resources.

            - user_id (or sometimes staff_user_id or provider_user_id) will be a request argument
                - if user_id is now part of the url params or payload, the endpoint should be limited
                to only accessing the resources off the logged-in user
            - 'staff_self' will be in user_type

            Using these two pieces of info, we will just check that the logged-in
            user is the same as the user being requested in the request argument
            (user_id, staff_user_id, or provider_user_id)

        3.  Provider is accessing client's resources. There are two classes of staff roles in our system: provider
            and staff roles. Each set of roles are mutually exclusive. Provider roles engage with clients
            as medical/professional service providers. Staff roles are internal and serve to aid providers
            and clients in using the modobio platform (e.g. community_manger, client_services, staff_admin).
            For provider roles here are the authorization checks:

                    a.  There are no role or resource checks specified. Just being a provider
                        member grants access to endpoint.
                    b.  Only ``staff_role`` is specified. Staff member must meet role
                        requirements for all request methods.
                    c.  Only resources are specified. Check against resources authorized
                        through the clinical care team system. All request methods allowed
                        if resource access check passes.
                    d.  Both resources and ``staff_role`` are specified. Check against
                        resources authorized through the clinical care team system. If the
                        request method is not GET, provider must also meet role requirements,
                        e.g. only medical_doctor role may view and edit blood test results
                        for a client.
                
        """
        # bring up the roles for the staff member
        staff_user_roles = db.session.query(StaffRoles.role).filter(StaffRoles.user_id==user.user_id).all()
        staff_user_roles = [x[0] for x in staff_user_roles]

        requested_user_id =  request.view_args.get(
            'user_id', 
                request.view_args.get('client_user_id', 
                    request.view_args.get('staff_user_id',
                        request.view_args.get('provider_user_id',None))))

        if len(staff_user_roles) == 0:
            raise Unauthorized("Provider does not have any roles")
        # provider accessing their own resources
        # request args will either contain uid or staff_uid which must match the logged-in user
        # if logged-in staff is not the user being requested and no role nor resource requirements are provided, raise unauthorized

        if 'staff_self' in self.user_type \
            and requested_user_id == user.user_id:
            return

        # if requested user is not the logged-in user and no role nor resource requirements are provided, raise unauthorized
        elif 'staff_self' in self.user_type \
            and requested_user_id not in (None, user.user_id) \
            and self.staff_role is None \
            and len(self.resources) == 0:
                raise Unauthorized

        # check if resource access check is necessary
        if len(self.resources) > 0:
            if not requested_user_id:
                raise BadRequest("No user specified")
            # 1. Check if staff member has resource access
            # 2. if request method is not GET, verify role access

            # set the context and successful authorizations list in the g object
            g.clinical_care_context = True
            g.clinical_care_authorized_resources = []
            # search db for this resource authorization
            for resource in self.resources:
                is_authorized = db.session.query(
                        ClientClinicalCareTeamAuthorizations.resource_id, LookupClinicalCareTeamResources.resource_name
                    ).filter(ClientClinicalCareTeamAuthorizations.team_member_user_id == user.user_id
                    ).filter(ClientClinicalCareTeamAuthorizations.user_id == requested_user_id
                    ).filter(ClientClinicalCareTeamAuthorizations.resource_id == LookupClinicalCareTeamResources.resource_id
                    ).filter(LookupClinicalCareTeamResources.resource_name == resource
                    ).filter(ClientClinicalCareTeamAuthorizations.status == 'accepted'
                    ).all()
                if len(is_authorized) == 1:
                    g.clinical_care_authorized_resources.append(resource)
                    continue
            if len(g.clinical_care_authorized_resources) == 0:
                # this user does not have access to any resource in this endpoint
                raise Unauthorized

            # any role may be granted read only access to client resources
            # only specific roles may be granted write access to client resources
            if self.staff_role is not None and request.method != 'GET':
                if not any(role in staff_user_roles for role in self.staff_role):
                    raise Unauthorized

        # No team resource requirements, must meet role requirements if specified
        elif self.staff_role is not None:
            if not any(role in staff_user_roles for role in self.staff_role):
                raise Unauthorized

        # Staff is accessing client resources without role or resource authorization
        else:
            logger.debug(f'Staff user granted access to endpoint without checks: {request.path}')
            return

        # authorization checks all end here
        return


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
            
        user_details = db.session.execute(
            select(User, UserLogin)
            .join(
                UserLogin,
                User.user_id == UserLogin.user_id)
            .where(
                User.email == username.lower())
        ).one_or_none()

        # make sure login details exist, check password
        if not user_details:
            db.session.add(UserTokenHistory(event='login', ua_string=request.headers.get('User-Agent')))
            db.session.commit()
            raise Unauthorized

        user, user_login = user_details

        if check_password_hash(user_login.password, password):
            user_login.last_login = DB_SERVER_TIME
            db.session.commit()
            db.session.refresh(user_login)
            return user, user_login, 'basic_auth'
        else:
            db.session.add(UserTokenHistory(event='login', user_id=user.user_id, ua_string=request.headers.get('User-Agent')))
            db.session.commit()
            raise Unauthorized

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

    def verify_token(self, token):
        ''' verify_token is a method that is used as a decorator to store 
            the token checking process that is defined in auth.py '''
        if not token:
            raise Unauthorized

        # decode and validate token 
        secret = current_app.config['SECRET_KEY']
        try:
            decoded_token = jwt.decode(token, secret, algorithms='HS256')
        # Capture all possible JWT errors
        except jwt.exceptions.PyJWTError:
            raise Unauthorized

        # ensure token is an access token type
        if decoded_token['ttype'] != 'access':
            raise Unauthorized

        user, user_login = db.session.execute(
            select(User, UserLogin)
            .join(
                UserLogin,
                User.user_id == UserLogin.user_id)
            .where(
                User.user_id == decoded_token['uid'])
        ).one_or_none()

        g.user_type = decoded_token.get('utype')
        return user, user_login, decoded_token.get('utype')

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
        return self.verify_token(token)

# simple authentication handler allows password authentication and
# stores a current user for view functions to check against
basic_auth = BasicAuth()
token_auth = TokenAuth()
