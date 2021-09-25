import logging

from werkzeug.exceptions import InternalServerError, HTTPException, NotFound
from werkzeug.http import HTTP_STATUS_CODES

from odyssey.api import api

logger = logging.getLogger(__name__)



#############################################################################
class UserNotFound(HTTPException):
    """in the case a non-existent client is being requested"""
    def __init__(self, user_id=None, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = f'The client with user_id {user_id}, does not exist. Please try again.'

        self.code = 404

class ExamNotFound(HTTPException):
    """in the case a non-existent client is being requested"""
    def __init__(self, examid, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = f'The exam with id {examid}, does not exist. Please try again.'

        self.code = 404

class TransactionNotFound(HTTPException):
    """in the case a non-existent client is being requested"""
    def __init__(self, idx, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = f'The transaction with id {idx}, does not exist. Please try again.'

        self.code = 404

class ContentNotFound(HTTPException):
    """in the case a non-existent resource is requested"""
    def __init__(self):
        super().__init__(description=message)
        
        self.message = ""
        
        self.code = 204


class MethodNotAllowed(HTTPException):
    """ Exception for the case a resource already exists in response to a POST request. """
    def __init__(self, *args, message='', **kwargs):
        super().__init__(*args, **kwargs)
        if message:
            self.message = message
        else:
            self.message = 'The resource already exists. Use PUT to edit existing resources.'
        self.code = 405


class ClientDeniedAccess(HTTPException):
    """ Exception for the case a client denied access
        to a 3rd party resource in an OAuth request.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = 'Client denied access.'
        self.code = 409


class UnknownError(HTTPException):
    """ Exception for an unknown error. """
    def __init__(self, *args, message='', **kwargs):
        super().__init__()
        if message:
            self.message = message
        else:
            self.message = 'Unknown error occured'
        self.code = 400

class InputError(HTTPException):
    """ Exception raised for errors with the input.

        Attributes:
        expression -- input expression in which the error occurred
        status_code -- Common status code for specific error
        message -- explanation of the error
    """
    def __init__(self, status_code=None, message=''):
        super().__init__()
        if message:
            self.description = message
        else:
            self.description = 'Input error'
        
        if status_code:
            self.code = status_code
        else:
            self.code = 400

class ContentNotFoundReturnData(HTTPException):
    """Special case for when a resource has not yet been created but the client must see other data to proceed"""
    def __init__(self, data=None, user_id = None):
        super().__init__(description=message)
        data.update({"user_id": user_id})
        self.code = 200
        self.message = "no instance of resource exists yet"

        self.data = data

class UnauthorizedUser(HTTPException):
    """in the case a staff member is trying to access resources they are not permitted to"""
    def __init__(self, email=None, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = f'The staff member with email {email}, Is not authorized'

        self.code = 401


class ClientAlreadyExists(HTTPException):
    """in the case a staff member is trying to create a new client when the client already exists"""
    def __init__(self, identification=None, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = f'The client identified by, {identification} already exists.'

        self.code = 409

class MedicalConditionNotFound(HTTPException):
    """Used if a medical condition is not found"""
    def __init__(self, medical_condition_id, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = f'The medical condition with id, {medical_condition_id} does not exists.'

        self.code = 409

class STDNotFound(HTTPException):
    """Used if a STD is not found in DB"""
    def __init__(self, std_id, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = f'The STD with id, {std_id} does not exist.'

        self.code = 409

class MedicalConditionAlreadySubmitted(HTTPException):
    """Used if a medical condition is already submitted for a user"""
    def __init__(self,user_id, medical_condition_id, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = f'The user, {user_id}, already submitted medical condition with id, {medical_condition_id}.'

        self.code = 409

class RelationAlreadyExists(HTTPException):
    """in the case a client is trying to be associated with a facility where this relationship is already defined"""
    def __init__(self, client_identification=None, facility_identification=None, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = f'The client identified by, {client_identification} is already associated with the facility identified by {facility_identification}.'
        self.code = 409

class StaffEmailInUse(HTTPException):
    """in the case a staff member is creating a staff account with the same email"""
    def __init__(self, email, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = f'The email, {email} is already in use for a staff account.'

        self.code = 409

class ClientEmailInUse(HTTPException):
    """in the case a staff member is creating a client account with the same email"""
    def __init__(self, email, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = f'The email, {email} is already in use for a client account.'

        self.code = 409


class ClientNotFound(HTTPException):
    """in the case a staff member is trying to edit a client that does not exist"""
    def __init__(self, identification=None, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = f'The client identified by, {identification} does not exit. Try another identification or create a new client.'

        self.code = 404

class TestNotFound(HTTPException):
    """in the case that blood test results are requested for a test id that does not exist"""
    def __init__(self, identification=None, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = f'The blood test identified by, {identification} does not exit.'

        self.code = 404

class ResultTypeNotFound(HTTPException):
    """in the case that blood test result type is given where that result type does not exist"""
    def __init__(self, identification=None, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = f'The blood test resultType identified by, {identification} does not exit.'

        self.code = 404

class FacilityNotFound(HTTPException):
    """in the case a staff member is trying to edit a client that does not exist"""
    def __init__(self, identification=None, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = f'The facility identified by, {identification} does not exit. Try another identification or create a new registered facility.'

        self.code = 404

class DrinkNotFound(HTTPException):
    """in the case that drink_id is given where that drink_id does not exist"""
    def __init__(self, identification=None, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = f'The drink identified by, {identification} does not exit.'

        self.code = 404

class IllegalSetting(HTTPException):
    """in the case an API request includes a setting or parameter that is not allowed"""
    def __init__(self, param=None, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = f'Illegal Setting of parameter, {param}. You cannot set this value manually'

        self.code = 400

class InsufficientInputs(HTTPException):
    """in the case that the input does not have enough data"""
    def __init__(self, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = 'Insufficient inputs supplied. At least 1 value other than date (and idx for PUT) must be given.'

        self.code = 405

class StaffNotFound(HTTPException):
    """in the case a non-existent staff member is being requested"""
    def __init__(self, user_id=None, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = f'The Staff member with user_id {user_id}, does not exist. Please try again.'

        self.code = 404

class LoginNotAuthorized(HTTPException):
    """Used for auth.py if a user does not have certain authorizations
       for using the ModoBio APIs"""
    def __init__(self, message = ''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = 'Not Authorized'

        self.code = 401

class EmailNotVerified(HTTPException):
    """Used for auth.py if a user has not yet verified their email."""
    def __init__(self):
        super().__init__(description=message)
        self.message = "User email address has not yet been verified"

        self.code = 401

class GenericNotFound(HTTPException):
    """
    When requesting an item from the database which does not exist
    """
    def __init__(self, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = 'Not Found'

        self.code = 404

class MissingThirdPartyCredentials(HTTPException):
    """The server is has not been configured with the necessary credentials to access a third party API"""
    def __init__(self, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = "Credentials for 3rd party service are missing"

        self.code = 500

class InvalidVerificationCode(HTTPException):
    """
    In the case that an email verification is requested but the wrong code is
    given or the code's lifetime has expired
    """
    def __init__(self, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = "Invalid email verification code."

        self.code = 403

class TooManyPaymentMethods(HTTPException):
    """
    In the case that a payment method is trying to be added for a user who
    already has at least 5 saved payment methods
    """

    def __init__(self, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = "The designated user already has at least 5 saved payment methods. Please delete a method in order to add a new one."

        self.code = 405

class DisabledEndpoint(HTTPException):
    """
    In the case an endpoint should be disabled but the code should remain
    in order to reenable the endpoint in the future.
    """

    def __init__(self, message=''):
        super().__init__(description=message)
        if message:
            self.message = message
        else:
            self.message = "This endpoint is disabled until further notice."

        self.code = 403

class GenericThirdPartyError(HTTPException):
    """
    In the case that a third party api returns an error code.
    """

    def __init__(self, status_code = None, message=''):
        if message:
            self.message = message
        else:
            self.message = "Third party api returned an error."

        if status_code:
            self.code = status_code
        else:
            self.code = 400

########################################################################

@api.errorhandler(HTTPException)
def http_exception_handler(error) -> tuple:
    """ Create a JSON response from any HTTPException.

    :class:`werkzeug.exceptions.HTTPException`s are handled by default by flask-restx,
    but this handler adds extra information to the error response. It also logs the
    error, including the error traceback. It is logged at the :attr:`logging.INFO` level,
    because it is a handled error, i.e. the message is forwarded to the user.

    This handles :class:`werkzeug.exceptions.HTTPException`s and **all it's subclasses**.

    Params
    ------
    error : :class:`werkzeug.exceptions.HTTPException`
        The error raised in the code. Must be a subclass of :class:`werkzeug.exceptions.HTTPException`.
        If an extra parameter ``data`` (``dict``) exists on the error object, it will be merged into
        the response.

    Returns
    -------
    dict
        Response as dict, flask-restx will turn it into JSON.

    int
        HTTP status code for error.
    """
    response = getattr(error, 'data', {})
    response['status_code'] = error.code
    response['message'] = error.description
    response['error'] = HTTP_STATUS_CODES.get(error.code, 'Unknown error')
    logger.info(error.description, exc_info=True)
    return response, error.code

@api.errorhandler(Exception)
def exception_handler(error):
    """ Create a JSON response from any :class:`Exception` that is not handled by :func:`http_exception_handler`.

    Flask usuaslly turns any unhandled :class:`Exception` into a
    :class:`werkzeug.exceptions.InternalServerError`, but does not provide any further
    information as to where the exception was raised. This handler returns a 500
    (Internal server error) as expected, but also logs the error with traceback.
    It is logged at :attr:`logging.ERROR` level, because it is an unhandled error,
    i.e. something unexpected went wrong in the background and the user does not
    need to be informed what that is.

    This handles :class:`Exception`s and **all it's subclasses**, that are not otherwise
    handled by :func:`http_exception_handler`.

    Params
    ------
    error : :class:`Exception`
        The error raised in the code. If an extra parameter ``data`` (``dict``) exists on the
        error object, it will be merged into the response.

    Returns
    -------
    dict
        Response as dict, flask-restx will turn it into JSON.

    int
        HTTP status code. Always 500, internal server error.
    """
    response = getattr(error, 'data', {})
    response['status_code'] = 500
    response['message'] = 'Internal server error'
    response['error'] = 'Internal server error'
    logger.exception(error, stack_info=True)
    return response, 500
