"""Utility functions for the odyssey package."""

import ast
import functools
import inspect
import logging
import random
import re
import statistics
import textwrap
import typing as t
from datetime import datetime, time, timedelta
from time import monotonic

import jwt
import terra
from dateutil import parser
from flask import current_app, request, url_for
from pytz import utc
from sqlalchemy import select
from werkzeug.exceptions import BadRequest, Unauthorized

from odyssey import db, mongo
from odyssey.api.client.models import (
    ClientConsent, ClientConsultContract, ClientFacilities, ClientIndividualContract,
    ClientPolicies, ClientRelease, ClientSubscriptionContract
)
from odyssey.api.community_manager.models import \
    CommunityManagerSubscriptionGrants
from odyssey.api.doctor.models import MedicalBloodTests, MedicalImaging
from odyssey.api.facility.models import RegisteredFacilities
from odyssey.api.lookup.models import *
from odyssey.api.lookup.models import (LookupBookingTimeIncrements, LookupSubscriptions)
from odyssey.api.notifications.models import Notifications
from odyssey.api.telehealth.models import TelehealthBookings
from odyssey.api.user.models import (
    User, UserPendingEmailVerifications, UserProfilePictures, UserRemovalRequests,
    UserSubscriptions, UserTokenHistory
)
from odyssey.api.user.schemas import UserSubscriptionsSchema
from odyssey.api.wearables.models import WearablesV2
from odyssey.integrations.apple import AppStore
from odyssey.integrations.terra import TerraClient
from odyssey.utils import search
from odyssey.utils.auth import token_auth
from odyssey.utils.constants import (ALPHANUMERIC, DB_SERVER_TIME, EMAIL_TOKEN_LIFETIME)
from odyssey.utils.files import FileDownload
from odyssey.utils.message import send_email

logger = logging.getLogger(__name__)


def generate_modobio_id(user_id: int, firstname: str = None, lastname: str = None) -> str:
    """Generate the user's mdobio_id.

    The modo bio identifier is used as a public user id, it
    can also be exported to other healthcare providers (clients only).
    It is made up of the firstname and lastname initials and 10 random alphanumeric
    characters.

    Parameters
    ----------
    firstname : str
        Client first name.

    lastname : str
        Client last name.

    user_id : int
        User ID number.

    Returns
    -------
    str
        Medical record ID
    """
    rli_hash = ''.join([random.choice(ALPHANUMERIC) for i in range(10)])

    if all((firstname, lastname)):
        salt = firstname[0] + lastname[0]
    else:
        raise BadRequest('Missing first and/or last name.')
    return (salt + rli_hash).upper()


def list_average(values_list):
    """Helper function to clean list values before attempting to find the average"""
    # remove empty items
    values_list_ = [val for val in values_list if val is not None]
    if len(values_list_) > 0:
        return statistics.mean(values_list_)
    else:
        return None


def check_client_existence(user_id):
    """Check that the client is in the database
    All clients must be in the CLientInfo table before any other procedure"""
    client = User.query.filter_by(user_id=user_id, is_client=True, deleted=False).one_or_none()
    if not client:
        raise Unauthorized
    return client


def check_staff_existence(user_id):
    """Check that the user is in the database and is a staff member"""
    staff = User.query.filter_by(user_id=user_id, is_staff=True, deleted=False).one_or_none()
    if not staff:
        raise Unauthorized
    return staff


def check_provider_existence(user_id):
    """Check that the user is in the database and is a staff member"""
    staff = User.query.filter_by(user_id=user_id, is_provider=True, deleted=False).one_or_none()
    if not staff:
        raise Unauthorized
    return staff


def check_user_existence(user_id, user_type=None):
    """Check that the user is in the database
    If user_type is 'client', check if user_id exists in ClientInfo table.
    If user_type is 'staff', check if user_id exists in StaffProfile table.
    If user_type is neither of the above, just check if user_id exists in User table.
    """
    if user_type == 'client':
        user = User.query.filter_by(user_id=user_id, is_client=True, deleted=False).one_or_none()
    elif user_type == 'staff':
        user = User.query.filter_by(user_id=user_id, is_staff=True, deleted=False).one_or_none()
    else:
        user = User.query.filter_by(user_id=user_id, deleted=False).one_or_none()
    if not user:
        raise Unauthorized
    return user


def check_blood_test_existence(test_id):
    """Check that the blood test is in the database"""
    test = MedicalBloodTests.query.filter_by(test_id=test_id).one_or_none()
    if not test:
        raise BadRequest(f'Blood test {test_id} not found.')


def check_blood_test_result_type_existence(result_name):
    """Check that a supplied blood test result type is in the database"""
    result = LookupBloodTestResultTypes.query.filter_by(result_name=result_name).one_or_none()
    if not result:
        raise BadRequest(f'Blood test result {result_name} not found.')


def fetch_facility_existence(facility_id):
    facility = RegisteredFacilities.query.filter_by(facility_id=facility_id).one_or_none()
    if not facility:
        raise BadRequest(f'Facility {facility_id} not found.')
    return facility


def check_client_facility_relation_existence(user_id, facility_id):
    relation = ClientFacilities.query.filter_by(
        user_id=user_id, facility_id=facility_id
    ).one_or_none()
    if relation:
        raise BadRequest(f'Client already associated with facility {facility_id}.')


def check_medical_condition_existence(medcon_id):
    medcon = LookupMedicalConditions.query.filter_by(medical_condition_id=medcon_id).one_or_none()
    if not medcon:
        raise BadRequest(f'Medical condition {medcon_id} not found.')


# def check_drink_existence(drink_id):
#     drink = LookupDrinks.query.filter_by(drink_id=drink_id).one_or_none()
#     if not drink:
#         raise BadRequest(f'Drink {drink_id} not found.')


def check_std_existence(std_id):
    std = LookupSTDs.query.filter_by(std_id=std_id).one_or_none()
    if not std:
        raise BadRequest(f'STD {std_id} not found.')


def verify_jwt(token, error_message='', refresh=False):
    """
    Ensure token is signed correctly and is not yet expired
    Returns the token's payload
    """
    secret = current_app.config['SECRET_KEY']
    try:
        decoded_token = jwt.decode(token, secret, algorithms='HS256')
    except:
        # log the refresh attempt
        if refresh:
            token_payload = jwt.decode(token, options={'verify_signature': False})
            db.session.add(
                UserTokenHistory(
                    user_id=token_payload.get('uid'),
                    event='refresh',
                    ua_string=request.headers.get('User-Agent'),
                )
            )
            db.session.commit()

        raise Unauthorized(error_message)

    return decoded_token


class DecoratorVisitor(ast.NodeVisitor):
    """Find decorators placed on functions or classes."""

    decorators = []

    def visit_FunctionDef(self, node):
        """For a node that is a :class:`ast.FunctionDef`, collect its decorators."""
        self.decorators.extend(node.decorator_list)

    def visit_ClassDef(self, node):
        """For a node that is a :class:`ast.ClassDef`, collect its decorators."""
        self.decorators.extend(node.decorator_list)


def find_decorator_value(
    function: t.Callable,
    decorator: str,
    argument: int = None,
    keyword: str = None,
) -> t.Any:
    """Return the value of an argument or keyword passed to a decorator placed on a function or class.

    For example, in the code

    .. code:: python

        class SomeEndpoint(BaseResource):
            @accepts(schema=SomeSchema)
            def post(self):
                ...

        schema = find_decorator_value(SomeEndpoint.post, decorator='accepts', keyword='schema')

    :func:`find_decorator_value` will find the decorator :func:`accepts` which is decorating
    :func:`post()` and return the value ``SomeSchema`` passed to the argument :attr:`schema`.

    This function can also find positional arguments passed into the decorator

    .. code:: python

        class SomeEndpoint(BaseResource):
            # incorrect use of @accepts for this example only
            @accepts('x', 3, SomeSchema)
            def post(self):
                ...

        schema = find_decorator_value(SomeEndpoint.post, decorator='accepts', argument=2)

    will return the same ``SomeSchema`` object as the first example.

    Parameters
    ----------
    function : Callable
        A function, method, or class which has a decorator on it.

    decorator : str
        The name of the decorator to search for.

    argument : int
        The index of the positional argument passed into the decorator. Mutually exclusive
        with the ``keyword`` argument, must provide exactly one.

    keyword : str
        The name of the keyword argument passed into the decorator. Mutually exclusive
        with the ``argument`` argument, must provide exactly one.

    Returns
    -------
    Any
        The value of the parameter as passed into the decorator. Can be any Python object.

    Raises
    ------
    ValueError
        Raised when called with incorrect arguments.

    TypeError
        Raised when :attr:`decorator` is not found or when :attr:`argument` or :attr:`keyword`
        are not found in the decorator.
    """
    # Check parameters
    if (keyword is None and argument is None) or (keyword is not None and argument is not None):
        raise ValueError('You must provide exactly one of "keyword" or "argument".')

    if argument is not None and not isinstance(argument, int):
        raise ValueError('Parameter "argument" must be integer.')

    if keyword is not None and not isinstance(keyword, str):
        raise ValueError('Parameter "keyword" must be string.')

    if decorator.startswith('@'):
        decorator = decorator[1:]

    # Get actual function, not the one wrapped by a decorator
    top_func = inspect.unwrap(function)

    # Get source code of function/class definition, convert to AST representation.
    extralines = []
    if inspect.isclass(top_func):
        # inspect.getsource(classobj) does NOT include decorators, unlike functions and methods.
        # Get previous lines if any of them include '@'
        wholefile, lineno = inspect.findsource(top_func.__class__)
        lineno -= 1
        while lineno >= 0:
            line = wholefile[lineno].strip()
            if line.startswith('@'):
                extralines.append(wholefile[lineno])
                lineno -= 1
                continue

            # It is legal to intersperse decorators with empty lines and comments.
            # Keep searching in that case.
            if not line or line.startswith('#'):
                lineno -= 1
                continue

            break

    code = inspect.getsource(top_func)
    code = '\n'.join(extralines) + code
    code = textwrap.dedent(code)
    tree = ast.parse(code)

    # Find decorators
    visitor = DecoratorVisitor()
    visitor.visit(tree)

    # Decorators can be called in 4 different ways.
    # Each way is represented differently in AST.
    #
    # 1. @aaa               Name(id='aaa')
    # 2. @aaa(1, kw=2)      Call(func=Name(id='aaa'),
    #                           args=[Constant(value=1)],
    #                           keywords=[keyword(arg='kw', value=Constant(value=2))])
    # 3. @AAA.aaa           Attribute(value=Name(id='AAA'), attr='aaa')
    # 4. @AAA.aaa(1, kw=2)  Call(func=Attribute(value=Name(id='AAA'), attr='aaa'),
    #                           args=[Constant(value=3)],
    #                           keywords=[keyword(arg='kw', value=Constant(value=2)))

    # Map decorator names to AST nodes
    decos = {}
    for deco in visitor.decorators:
        if isinstance(deco, ast.Name):
            deco_name = deco.id
        elif isinstance(deco, ast.Attribute):
            deco_name = deco.value.id + '.' + deco.attr
        elif isinstance(deco, ast.Call):
            if isinstance(deco.func, ast.Name):
                deco_name = deco.func.id
            elif isinstance(deco.func, ast.Attribute):
                deco_name = deco.func.value.id + '.' + deco.func.attr
            else:
                raise TypeError(f'Unknown decorator Call type found {deco}.')
        else:
            raise TypeError(f'Unknown decorator type found {deco}.')

        decos[deco_name] = deco

    if decorator not in decos:
        raise TypeError(f'Decorator {decorator} not found on {function}.')

    # Continue with the requested decorator
    deco = decos[decorator]

    # Find the AST node that represents either the argument or the keyword value.
    value = None
    if argument is not None:
        if not hasattr(deco, 'args'):
            raise TypeError(f'Decorator @{deco_name} has no positional arguments.')

        try:
            value = deco.args[argument]
        except IndexError:
            argno = len(deco.args)
            raise TypeError(f'Decorator @{deco_name} has only {argno} argument(s).')
    else:
        if not hasattr(deco, 'keywords'):
            raise TypeError(f'Decorator @{deco_name} has no keyword arguments.')

        kws = {kw.arg: kw.value for kw in deco.keywords}
        if keyword not in kws:
            raise TypeError(f'Keyword {keyword} not found in decorator @{deco_name}.')

        value = kws[keyword]

    # Get actual object from AST node; this is where it gets really hard.
    #
    # At this point we have an AST representation of the value passed in to the
    # decorator, either by argument or by keyword. We want the actual object of
    # that value, not just the AST representation. I don't know how to get that.
    #
    # I tried to analyze the frame stack (inspect.stack()). Calling frames hold
    # references to objects in memory. However, the stack is linear going from
    # the main caller (__main__ or thread start or something similar) to the
    # current frame. Another decorator that was called and finshed is no longer
    # on the stack.
    #
    # For now this will return only a few simple cases. It will not raise an
    # error for missing cases as there are too many, simply return None.

    if isinstance(value, ast.Constant):
        # int, str, or None
        return value.value
    elif isinstance(value, (ast.List, ast.Tuple, ast.Set)):
        # Only support collections of Constant, nothing nested or more complicated.
        if not all([isinstance(elt, ast.Constant) for elt in value.elts]):
            return

        elts = [elt.value for elt in value.elts]
        if isinstance(value, ast.List):
            return elts
        elif isinstance(value, ast.Tuple):
            return tuple(elts)
        else:
            return set(elts)
    elif isinstance(value, ast.Dict):
        # Only support simple dicts where both keys and values are Constant.
        if not all([isinstance(elt, ast.Constant) for elt in value.keys + value.values]):
            return

        return {k.value: v.value for k, v in zip(value.keys, value.values)}
    elif isinstance(value, ast.Name):
        # Value is a variable name, which means it must be defined or imported.
        # See if it's defined in the globals section of the function/class
        # on which the decorator was placed.
        # TODO: widen search, maybe go up the tree to search in globals for nested
        # function/class definitions, all the way up to module.
        if value.id in top_func.__globals__:
            return top_func.__globals__[value.id]


def date_validator(date_string: str):
    """
    check if date string is a valid iso formatted date (no time)

    Returns
    ------
    str: date specified if it is valid, otherwise raises an error
    """
    import re

    regex = r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])'
    match_iso8601 = re.compile(regex).match
    try:
        if match_iso8601(date_string) is not None:
            return date_string
        else:
            # string does not match requirements
            raise BadRequest(
                'date requested is not formatted properly. Please use ISO'
                ' format YYYY-MM-DD'
            )
    except TypeError:
        raise BadRequest(
            'date requested is not formatted properly. Please use ISO format'
            ' YYYY-MM-DD'
        )


def iso_string_to_iso_datetime(date_string: str):
    """
    Convert iso string to an iso datetime object.

    Function Parameters
    ------
    date_string: str
        Input string to be converted. Can be either ISO format date (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z).

    Returns
    ------
    date: datetime
        Converted datetime object
    """
    import re

    regex = r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])$'
    match_iso8601 = re.compile(regex).match

    # ISO Date was passed in. Ex. '2023-01-01'. Need to append midnight to the date to use to filter MongoDB documents
    if match_iso8601(date_string) is not None:
        parsed_date = parser.parse(date_string)
        date = datetime.combine(parsed_date, time(0))
        return date
    # Full ISO timestamp passed in. Ex. '2023-01-01T00:00:00Z'
    else:
        date = parser.parse(date_string)
        return date


def get_time_index(target_time: datetime):
    """
    This function will return the index of the time window corresponding to the provided target_time
    as defined in the LookupBookingTimeIncrements table.

    In order to do this, we query to find the index where the current time falls in the range of
    start time <= current time < end time
    """
    if target_time.hour == 23 and target_time.minute >= 55:
        return LookupBookingTimeIncrements.query.all()[-1].idx
    else:
        return (
            LookupBookingTimeIncrements.query.filter(
                LookupBookingTimeIncrements.start_time <= target_time.time(),
                LookupBookingTimeIncrements.end_time > target_time.time(),
            ).one_or_none().idx
        )


class EmailVerification:
    """
    Class for handling email verification routines
    """
    def __init__(self) -> None:
        self.secret = current_app.config['SECRET_KEY']

    @staticmethod
    def generate_token(user_id: int) -> str:
        """
        Generate a JWT with the appropriate user type and user_id
        """

        secret = current_app.config['SECRET_KEY']

        return jwt.encode(
            {
                'exp': datetime.utcnow() + timedelta(hours=EMAIL_TOKEN_LIFETIME),
                'uid': user_id,
                'ttype': 'email_verification',
            },
            secret,
            algorithm='HS256',
        )

    @staticmethod
    def generate_code() -> str:
        """
        Generate a 4 digit code
        """
        return str(random.randrange(1000, 9999))

    def begin_email_verification(self, user: User, updating: bool, email: str = None) -> dict:
        """
        Email verification process creates an entry into the UserPendingEmailVerification table which stores
        the code and token used to verify new emails. If a user is updating their email address, the new email
        is temporarily stored in this table until the email is verified.

        Params
        ------
        user : User
        updating : bool
            denotes if the user is updating their email (true) or the email is being provided
            for the first time (false)
        email : str
            if provided, this email is stored in the UserPendingEmailVerifications entry

        Returns
        ------
        dict: email verification code, token, email, and user_id
        """
        # Check if email is already in use
        if email:
            if User.query.filter_by(email=email).one_or_none():
                raise BadRequest('Email in use')

        # check if there is already a Pending email verification entry
        pending_verification = UserPendingEmailVerifications.query.filter_by(user_id=user.user_id
                                                                            ).one_or_none()

        # if there is a pending verification, remove it and create a new one
        if pending_verification:
            db.session.delete(pending_verification)
            db.session.flush()

        # generate token and code for email verification
        token = self.generate_token(user.user_id)
        code = self.generate_code()

        # create pending email verification in db
        email_verification_data = {
            'user_id': user.user_id,
            'token': token,
            'code': code,
            'email': email,
        }

        verification = UserPendingEmailVerifications(**email_verification_data)
        db.session.add(verification)

        # send email to the user
        if updating:
            # send update email if user already had a verified email
            template = 'email-update'
        else:
            # send first time verify email if user did not have an email on file
            template = 'email-verify'

        link = url_for(
            'api.user_user_pending_email_verifications_token_api',
            token=token,
            _external=True,
        )

        send_email(
            template,
            user.email,
            name=user.firstname,
            verification_link=link,
            verification_code=code,
        )

        db.session.commit()

        return email_verification_data

    def check_token(self, token: str) -> UserPendingEmailVerifications:
        """
        checks email verification token (JWT)

        Params
        ------
        token : str
            JWT for email verification session

        Returns
        ------
        UserPendingEmailVerifications
        """
        try:
            jwt.decode(token, self.secret, algorithms='HS256')
        except jwt.ExpiredSignatureError:
            raise Unauthorized('Email verification token expired.')

        verification = UserPendingEmailVerifications.query.filter_by(token=token).one_or_none()

        if not verification:
            raise Unauthorized('Email verification token not found.')

        return verification

    def check_code(self, user_id: int, code: str) -> UserPendingEmailVerifications:
        """
        checks provided email verification code and then validates token stored in UserPendingEmailVerifications

        Params
        ------
        user_id: int
        code : str
            code provided to user by email

        Returns
        ------
        UserPendingEmailVerifications
        """

        verification = UserPendingEmailVerifications.query.filter_by(user_id=user_id).one_or_none()

        if not verification or verification.code != code:
            raise Unauthorized('Email verification failed.')

        # Decode and validate token. Code should expire the same time the token does.
        try:
            jwt.decode(verification.token, self.secret, algorithms='HS256')
        except jwt.ExpiredSignatureError:
            raise Unauthorized('Email verification token expired.')

        return verification

    def complete_email_verification(
        self, token: str = None, code: str = None, user_id: int = None
    ) -> None:
        """
        Check the provided token or code to validate new emails. If the account is new, a modobio_id is generated and
        User.email_verified is set to True.

        Verification occurs through one of two methods
        1. Token is provided. This token is emailed to the user as part of the email verification url. Using just the token validates the
        email, the user's identity, and checks that the user has completed this step within the time allotted.
        2.Verification using the provided code. Users will also revieve a code in their email to verify their emails. We use this code
        and the user's user_id to verify they are the owner of the email. We then check the token (stored in UserPendingEmailVerifications)
        to ensure the process is completed within the token's TTL

        Params
        ------
        token : str
            JWT encoding the TTL of the email verification routine and the identity of the user.
        code:
            Short code provided to the user's email. This code, the user's id, and the TTL on the token provide the verification
        user_id:
            required only if verifying email using the provided code
        """

        if token:
            verification = self.check_token(token)
        elif code and user_id:
            verification = self.check_code(user_id=user_id, code=code)
        else:
            raise BadRequest('Code or token not provided')

        user = User.query.filter_by(user_id=verification.user_id).one_or_none()

        # If account is new, update modobio_id, membersince, and set User.email_verified=True
        if user.email_verified == False:
            user.update({'email_verified': True})
            # Run active campaign operations for when a user verifies their email.
            # Only run active campaign operations in prod
            if not current_app.debug:
                from odyssey.tasks.tasks import update_active_campaign_tags

                tags = []
                # Add user type tags
                if user.is_client:
                    tags.append('Persona - Client')
                if user.is_staff:
                    tags.append('Persona - Provider')
                update_active_campaign_tags.delay(user.user_id, tags)
        elif verification.email:
            user.update({'email': verification.email})

        if user.modobio_id == None:
            md_id = generate_modobio_id(user.user_id, user.firstname, user.lastname)
            user.update({'modobio_id': md_id, 'membersince': DB_SERVER_TIME})

            # check for pending subscription grants on this email, add new user_id to subscription grant entries
        subscription_grants = (
            CommunityManagerSubscriptionGrants.query.filter_by(email=user.email.lower()).all()
        )
        for grant in subscription_grants:
            grant.subscription_grantee_user_id = user.user_id

        db.session.commit()

        # update subscription status
        # at this point, pending subscription grants will be applied to the user using their user_id
        if user.is_client:
            update_client_subscription(user.user_id)

        # code/token were valid, remove the pending request
        db.session.delete(verification)
        db.session.commit()

        return


def delete_staff_data(user_id):
    """Delete staff specific data.

    This function is called by :func:`delete_user` to delete staff specific files
    from S3 and rows in staff specific tables.

    Parameters
    ----------
    user_id : int
        User ID number for staff member to be deleted.
    """
    # Delete all staff profile pictures from S3.
    fd = FileDownload(user_id)
    paths = (
        db.session.execute(select(UserProfilePictures.image_path).filter_by(staff_user_id=user_id)
                          ).scalars().all()
    )
    for path in paths:
        fd.delete(path)

    # Get a list of all tables in database that have fields: client_user_id & staff_user_id
    # NOTE - Order matters, must delete these tables before those with user_id
    # to avoid problems while deleting payment methods
    tableList = db.session.execute(
        'SELECT distinct(table_name) from information_schema.columns          '
        "  WHERE column_name='staff_user_id' OR column_name='client_user_id';"
    ).fetchall()

    for table in tableList:
        # Do not delete from TelehealthBookings when deleting staff data
        if table.table_name == 'TelehealthBookings':
            continue
        else:
            db.session.execute(
                f'DELETE FROM "{table.table_name}" WHERE'
                f' staff_user_id={user_id};'
            )

    # Get a list of all staff-specific tables in database that have field: user_id
    tableList = db.session.execute(
        'SELECT distinct(table_name) from information_schema.columns          '
        "  WHERE column_name='user_id' and (table_name LIKE '%Staff%' or"
        " table_name LIKE '%Practitioner');"
    ).fetchall()

    # delete from staff specific tables where user_id is the user to be deleted
    for table in tableList:
        # added data_per_client table due to issues with the testing database
        if table.table_name not in (
            'User',
            'UserRemovalRequests',
            'UserLogin',
            'UserSubscriptions',
            'data_per_client',
        ):
            db.session.execute(
                'DELETE FROM "{}" WHERE user_id={};'.format(table.table_name, user_id)
            )

    # only delete staff subscription
    db.session.execute(
        f'DELETE FROM "UserSubscriptions" WHERE user_id={user_id} AND'
        ' is_staff=True'
    )

    db.session.commit()


def delete_client_data(user_id):
    """Delete client specific data.

    This function is called by :func:`delete_user` to delete client specific files
    from S3, telehealth booking details, status history, and rows in client specific
    tables.

    Parameters
    ----------
    user_id : int
        User ID number for client member to be deleted.
    """
    # wearablesV2 mongoDB deletion
    # do this first because we need some info from tables that are deleted below
    # get the wearables the user has registered
    wearables = WearablesV2.query.filter_by(user_id=user_id).all()

    # loop through each wearable the user has registered
    tc = TerraClient()
    for each_wearable in wearables:
        try:
            terra_user = tc.from_user_id(str(each_wearable.terra_user_id))
        except (terra.exceptions.NoUserInfoException, KeyError):
            # Terra-python (at least v0.0.7) should fail with NoUserInfoException
            # if terra_user_id does not exist in their system. However, it checks
            # whether response.json is empty, which is not empty in the case of an
            # error (it holds the error message and status). The next step in
            # terra.models.user.User.fill_in_user_info() is to access
            # response.json["user"] which does not exist and fails with KeyError.
            # In any case, we don't care that the terra_user_id is invalid, we
            # were going to delete it anyway.
            # 2023-01-10: Terra has been notified of this bug.
            pass
        else:
            response = tc.deauthenticate_user(terra_user)
            tc.status(response)

        mongo.db.wearables.delete_many({'user_id': user_id, 'wearable': each_wearable})

        logger.audit(
            f'User {user_id} account deleted, wearable {each_wearable} info'
            ' and data deleted.'
        )

    fd = FileDownload(user_id)

    # Go through all columns that store S3 paths. Delete files from S3.
    cols = (
        ClientConsent.pdf_path,
        ClientConsultContract.pdf_path,
        ClientPolicies.pdf_path,
        ClientRelease.pdf_path,
        ClientSubscriptionContract.pdf_path,
        ClientIndividualContract.pdf_path,
        MedicalImaging.image_path,
    )
    for col in cols:
        results = (db.session.execute(select(col).filter_by(user_id=user_id)).scalars().all())

        for path in results:
            if path:
                fd.delete(path)

    # This one is special, because it is identified by client_user_id
    paths = (
        db.session.execute(
            select(UserProfilePictures.image_path).filter_by(client_user_id=user_id)
        ).scalars().all()
    )
    for path in paths:
        if path:
            fd.delete(path)

    # TelehealthBookingDetails.images and .voice are identified by booking_id,
    # # so filter TelehealthBookings table and use relationships.
    # bookings = (db.session.execute(
    #     select(TelehealthBookings)
    #     .filter_by(client_user_id=user_id))
    #             .scalars()
    #             .all())
    # for booking in bookings:
    #     if booking.booking_details.voice:
    #         fd.delete(booking.booking_details.voice)
    #     if booking.booking_details.images:
    #         for path in booking.booking_details.images:
    #             if path:
    #                 fd.delete(path)

    # At this point, all files should be deleted from S3.
    # Double check that that's true, warn if not and delete rest.
    remaining = tuple(fd.bucket.objects.filter(Prefix=fd.prefix))
    if remaining:
        files = (r.key for r in remaining)
        files = '\n'.join(files)
        logger.warning(
            'Found the following files remaining in S3 bucket'
            f' {fd.bucket.name} after deleting all registered files for user'
            f' {user_id}:\n{files}'
        )
        for f in files:
            fd.delete(f)

    # Get a list of all tables in database that have fields: client_user_id & staff_user_id
    # NOTE - Order matters, must delete these tables before those with user_id
    # to avoid problems while deleting payment methods
    tableList = db.session.execute(
        'SELECT distinct(table_name) from information_schema.columns          '
        "  WHERE column_name='staff_user_id' OR column_name='client_user_id';"
    ).fetchall()

    # Delete lines with user_id in all other tables except "User" and "UserRemovalRequests"
    for table in tableList:
        db.session.execute(f'DELETE FROM "{table.table_name}" WHERE client_user_id={user_id};')

    # Get a list of all client-specific tables in database that have field: user_id
    tableList = db.session.execute(
        'SELECT distinct(table_name) from information_schema.columns          '
        "  WHERE column_name='user_id' and NOT (table_name LIKE '%Staff%' or"
        " table_name LIKE '%Practitioner');"
    ).fetchall()

    # Delete lines with user_id in all other tables except "User", "UserLogin", "UserRemovalRequests", and "data_per_client"
    for table in tableList:
        # added data_per_client table due to issues with the testing database
        if table.table_name not in (
            'User',
            'UserRemovalRequests',
            'UserLogin',
            'UserSubscriptions',
            'data_per_client',
        ):
            db.session.execute(
                'DELETE FROM "{}" WHERE user_id={};'.format(table.table_name, user_id)
            )

    # only delete client subscription
    db.session.execute(
        f'DELETE FROM "UserSubscriptions" WHERE user_id={user_id} AND'
        ' is_staff=False'
    )

    db.session.commit()


def delete_user(user_id, requestor_id, delete_type):
    """
    This function is used to delete a user and any relevant user date. It is leveraged by the system
    admin delete user endpoint and (in the future) the task that automatically deletes accounts that have
    been marked as 'closed' for at least 30 days.

    Args:
        user_id (int): int id of the user to be deleted
        requestor_id (int): id of the user requesting to delete this user
        staff_delete (str): denotes what type of delete to do. Can be 'client', 'staff', or 'both'.
    """
    check_user_existence(user_id, requestor_id)

    user = User.query.filter_by(user_id=user_id).one_or_none()

    # save user email before it is nulled so we can send email after everything is done
    user_email = user.email

    requester = token_auth.current_user()[0]
    removal_request = UserRemovalRequests(
        requester_user_id=requester.user_id,
        user_id=user.user_id,
        removal_type=delete_type,
    )

    db.session.add(removal_request)
    db.session.flush()

    if user.was_staff:
        # cases where the user is either only staff or client and staff

        # staff users must always retain name, modobio_id, and user_id
        user.phone_number = None
        if delete_type == 'both':
            user.phone_number = None
            user.email = None
            user.deleted = True
            user.is_staff = False
            user.is_client = False
            delete_client_data(user_id)
            delete_staff_data(user_id)

            # since entire user is being deleted, we can delete the login info
            db.session.execute(f'DELETE FROM "UserLogin" WHERE user_id={user_id};')

            # remove user from elastic search indices (must be done after commit)
            search.delete_from_index(user_id)
        elif delete_type == 'client':
            delete_client_data(user_id)
            user.is_client = False
        elif delete_type == 'staff':
            delete_staff_data(user_id)
            if not user.is_client:
                # user was only staff, so we can delete the login info
                db.session.execute(f'DELETE FROM "UserLogin" WHERE user_id={user_id};')
                user.phone_number = None
                user.email = None
                user.deleted = True

                # remove user from elastic search indices (must be done after commit)
                search.delete_from_index(user_id)

            user.is_staff = False
        else:
            raise BadRequest('Invalid delete type.')
    else:
        # cases where the user is only a client user
        if delete_type in ('client', 'both'):
            user.email = None
            user.firstname = None
            user.middlename = None
            user.lastname = None
            user.phone_number = None
            user.deleted = True
            user.is_client = False
            delete_client_data(user_id)

            db.session.execute(f'DELETE FROM "UserLogin" WHERE user_id={user_id};')

            # remove user from elastic search indices (must be done after commit)
            search.delete_from_index(user_id)
    db.session.commit()

    # Send notification email to user being deleted.
    # Also send to user requesting deletion when DEPLOYMENT_ENV=production
    if user_email != requester.email:
        send_email('account-deleted', requester.email, user_email=user_email)

    send_email('account-deleted', user_email, user_email=user_email)


def create_notification(
    user_id,
    severity_id,
    notification_type_id,
    title,
    content,
    persona_type,
    expires=None,
):
    # used to create a notification

    notification = Notifications(
        **{
            'user_id': user_id,
            'title': title,
            'content': content,
            'severity_id': severity_id,
            'notification_type_id': notification_type_id,
            'persona_type': persona_type,
            'expires': expires,
        }
    )

    db.session.add(notification)


def update_client_subscription(
    user_id: int,
    latest_subscription: UserSubscriptions = None,
    apple_original_transaction_id: str = None,
):
    """
    Handles logic around updating a user's subscription.

    Subscriptions may originate from the app store or have been granted to the user by a community manager. We
    need to check both sources of subscriptions when updating a client subscription status. If both subscriptions
    exist, we take the app store subscription first before activating a subscription grant. Grants will remain in the
    CommunityManagerSubscriptionGrants table indefinitely and can be activated at any time by inserting a row into the
    UserSubscriptions table referring the subscription grant entry (UserSubscriptions.sponsorship_id).

    When updating a user's subscription status, we first bring up the latest subscription. Here are the possible cases:

    1. User is currently unsubscribed or their subscription has just expired.
        Create new subscription entry using details from the app store or internal subscription grants. If there are no
        subscriptions available then create and entry into the UserSubscriptions table with a status of 'unsubscribed'.
    2. User currently subscribed
        Check the app store to see if the subscription has been revoked.

    """
    if not latest_subscription:
        latest_subscription = (
            UserSubscriptions.query.filter_by(user_id=user_id, is_staff=False).order_by(
                UserSubscriptions.idx.desc()
            ).first()
        )

        # verify the user is a client and has a verified email
        user = User.query.filter_by(user_id=user_id).one_or_none()
        if not user.is_client:
            raise BadRequest('User is not a client.')
        if not user.email_verified:
            raise BadRequest('User email is not verified.')

    new_sub_data = {}
    utc_time_now = datetime.utcnow()
    welcome_email = False

    if (
        latest_subscription.subscription_status == 'subscribed'
        and latest_subscription.expire_date < utc_time_now
    ):
        # update current subscription to unsubscribed
        latest_subscription.update({
            'end_date': utc_time_now.isoformat(),
            'subscription_status': 'unsubscribed',
            'last_checked_date': utc_time_now.isoformat(),
        })
        # new subscription entry for unsubscribed status.
        # Can be overwritten if a subscription is found in the app store or subscription grants
        new_sub_data = {
            'subscription_status': 'unsubscribed',
            'is_staff': False,
            'start_date': utc_time_now.isoformat(),
        }

    # check appstore first
    if (apple_original_transaction_id or latest_subscription.apple_original_transaction_id):
        appstore = AppStore()
        # use transaction_id provided if exists else the transaction_id used previously
        transaction_info, renewal_info, status = appstore.latest_transaction(
            apple_original_transaction_id if apple_original_transaction_id else latest_subscription.
            apple_original_transaction_id
        )

        if status == 'ACTIVE':
            if latest_subscription.subscription_status == 'subscribed':
                # subscription is active and hasn't expired yet
                latest_subscription.update({'last_checked_date': utc_time_now.isoformat()})
            else:
                new_sub_data = {
                    'subscription_status':
                        'subscribed',
                    'subscription_type_id':
                        LookupSubscriptions.query.filter_by(
                            ios_product_id=transaction_info.get('productId')
                        ).one_or_none().sub_id,
                    'is_staff':
                        False,
                    'apple_original_transaction_id': (
                        apple_original_transaction_id if apple_original_transaction_id else
                        latest_subscription.apple_original_transaction_id
                    ),
                    'last_checked_date':
                        utc_time_now.isoformat(),
                    'expire_date':
                        datetime.fromtimestamp(transaction_info['expiresDate'] / 1000,
                                               utc).replace(tzinfo=None).isoformat(),
                    'start_date':
                        datetime.fromtimestamp(transaction_info['purchaseDate'] / 1000,
                                               utc).replace(tzinfo=None).isoformat(),
                }
                latest_subscription.update({
                    'end_date': utc_time_now.isoformat(),
                    'last_checked_date': utc_time_now.isoformat(),
                })
                if latest_subscription.subscription_type_id == None:
                    welcome_email = True  # user was previously unsubscribed and now has a subscription

        # if status in grace period or retry period, update subscription status to subscribed to keep current subscription
        elif (
            status in ('RETRY', 'GRACE_PERIOD')
            and latest_subscription.subscription_status == 'unsubscribed'
        ):
            latest_subscription.update({
                'end_date': None,
                'subscription_status': 'subscribed',
            })

            new_sub_data = {}

        elif (
            status in ('REVOKED', 'EXPIRED')
            and latest_subscription.subscription_status == 'subscribed'
        ):
            # update current subscription to unsubscribed
            latest_subscription.update({
                'end_date': utc_time_now.isoformat(),
                'subscription_status': 'unsubscribed',
                'last_checked_date': utc_time_now.isoformat(),
            })
            # subscription has been revoked. Add new unsubscribed entry to UserSubscriptions
            new_sub_data = {
                'subscription_status': 'unsubscribed',
                'is_staff': False,
                'start_date': datetime.utcnow().isoformat(),
            }

        logger.info(f'Apple subscription updated for user_id: {user_id}')

    if (
        latest_subscription.subscription_status == 'unsubscribed'
        and new_sub_data.get('subscription_status') != 'subscribed'
    ):
        # check if the user has a subscription granted to them
        #  - bring up earliest unused subscription grant
        #  - if an unused sponsorship is found and the user is unsubscribed, add new subscription entry to UserSubscriptions
        #  - if an unused sponsorship is found and the user is subscribed, do nothing.
        subscription_grant = (
            CommunityManagerSubscriptionGrants.query.filter_by(
                subscription_grantee_user_id=user_id, activated=False
            ).order_by(CommunityManagerSubscriptionGrants.idx.asc()).first()
        )
        if subscription_grant:
            subscription_grant.activated = True
            new_sub_data = {
                'sponsorship_id':
                    subscription_grant.idx,
                'subscription_status':
                    'subscribed',
                'subscription_type_id':
                    subscription_grant.subscription_type_id,
                'is_staff':
                    False,
                'last_checked_date':
                    utc_time_now.isoformat(),
                'expire_date': (
                    utc_time_now + timedelta(
                        days=31 if subscription_grant.subscription_type_information.frequency ==
                        'Month' else 365
                    )
                ).isoformat(),
                'start_date':
                    utc_time_now.isoformat(),
            }
            latest_subscription.update({
                'end_date': utc_time_now.isoformat(),
                'last_checked_date': utc_time_now.isoformat(),
            })
            if latest_subscription.subscription_type_id == None:
                welcome_email = True  # user was previously unsubscribed and now has a subscription
    else:
        # user is subscribed and hasn't expired yet
        latest_subscription.update({'last_checked_date': utc_time_now.isoformat()})

    if new_sub_data.get('subscription_status'):
        new_sub = UserSubscriptionsSchema().load(new_sub_data)
        new_sub.user_id = user_id
        db.session.add(new_sub)

    if welcome_email:
        # send welcome email for new subscriptions
        user = User.query.filter_by(user_id=user_id).one_or_none()
        send_email('subscription-confirm', user.email, firstname=user.firstname)


def lru_cache_with_ttl(maxsize=128, typed=False, ttl=60):
    """Least-recently used cache with time-to-live (ttl) limit.

    This cache works just like :func:`functools.lru_cache`, but enhances it
    with a time-to-live (ttl) parameter. An item in the cache is updated only
    if it is older than ``ttl``. Any item that is not requested but it older
    than ``ttl`` is deleted from the cache. This only happens at the moment
    the cache is accessed, though.

    Use as a decorator::

        @lru_cache_with_ttl(ttl=20)
        def expensive_function():
            return something

    Parameters
    ----------
    maxsize : int, default = 128
        Maximum number of items in the cache. See :func:`functools.lru_cache`.

    typed : bool, default = False
        Decides whether arguments of different type are equivalent. See
        :func:`functools.lru_cache`.

    ttl : int, default = 60
        Time-to-live, in seconds, after which an item in the cache is considered
        expired.
    """

    # Idea from https://stackoverflow.com/a/71634221
    # Replaced Result class with a dict. Creation is ~4x faster
    # and both read from and assign to are ~20% faster.
    def decorator(func):
        @functools.lru_cache(maxsize=maxsize, typed=typed)
        def cached_func(*args, **kwargs):
            value = func(*args, **kwargs)
            expire = monotonic() + ttl
            logger.debug(
                f'Loading "{func!r}" ttl cache expire "{expire}" with value'
                f' "{value}"'
            )
            return {'value': value, 'expire': expire}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = cached_func(*args, **kwargs)
            if result['expire'] < monotonic():
                result['value'] = func(*args, **kwargs)
                result['expire'] = monotonic() + ttl
                logger.debug(
                    f'Reloading "{func!r}" expired ttl cache new expire'
                    f' "{result["expire"]}"with value "{result["value"]}"'
                )
            return result['value']

        wrapper.cache_clear = cached_func.cache_clear
        return wrapper

    return decorator


def create_wearables_filter_query(
    user_id: int,
    wearable: str,
    start_date: datetime,
    end_date: datetime,
    query_specificaiton: list,
):
    """
    Creates and formats the query to be passed into mongo to filter and specify the data wanting to be returned.

    Ex query :) db.wearables.find(
        {   //Filters the query
            'user_id': 1,
            "wearable": "FITBIT",
            'timestamp': {
                '$gte': start_date, '$lte': end_date
            },
            "data.Activity.heart_rate_data": { "$exists": true },
            "data.Activity.calories_data": { "$exists": true }
        },
        {   //Specifies what fields or/or data should be returned
            "user_id": 1,
            "timestamp": 1,
            "data.Activity.heart_rate_data": 1,
            "data.Activity.calories_data": 1
        })
    """

    filters = {
        'user_id': user_id,
        'wearable': wearable,
        'timestamp': {
            '$gte': start_date,
            '$lte': end_date
        },
    }
    # Data that should or shouldn't be included in final result.
    # Defaults to all fields
    specification = {}

    if len(query_specificaiton) > 0:
        # Validate
        valid_query_specification = re.compile(r'^[A-Za-z_.]*$')
        # must manually include these fields to be returned if specifying data
        specification['user_id'] = specification['timestamp'] = specification['wearable'] = 1

        for field in query_specificaiton:
            # validate only allowed characters are in the query specifcation.
            if not valid_query_specification.match(field):
                raise BadRequest(
                    'Invalid character in query_specification. Only letters,'
                    ' underscores, and periods allowed.'
                )

            # Format to filter if requested field exists in document
            if '$or' not in filters:
                filters['$or'] = [{field: {'$exists': True}}]
            else:
                filters['$or'].append({field: {'$exists': True}})

            # Set field to be included in result
            specification[field] = 1

    return filters, specification


def date_range(start_time: str, end_time: str, time_range: timedelta = timedelta(days=7)):
    """
    Generate a start and end range for wearables data retrieval.

    Parameters
    ----------
    start_time : str, optional
        ISO formatted date string
    end_time : str, optional
        ISO formatted date string
    time_range : timedelta, default=timedelta(days=7)
        A timedelta object representing the default duration of the data range.

    Returns
    -------
    tuple
        start_time and end_time datetime objects.
    """
    if start_time and end_time:
        start_time = iso_string_to_iso_datetime(start_time)
        end_time = iso_string_to_iso_datetime(end_time)
        if start_time > end_time:
            raise BadRequest('start_time must occur before end_time')
    elif start_time:
        start_time = iso_string_to_iso_datetime(start_time)
        end_time = start_time + time_range
    elif end_time:
        end_time = iso_string_to_iso_datetime(end_time)
        start_time = end_time - time_range
    else:
        end_time = datetime.utcnow()
        start_time = end_time - time_range

    return start_time, end_time
