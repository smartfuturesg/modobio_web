from werkzeug.http import HTTP_STATUS_CODES

from odyssey.api import api


class UserNotFound(Exception):
    """in the case a non-existent client is being requested"""
    def __init__(self, user_id=None, message = None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = f'The client with user_id {user_id}, does not exist. Please try again.'

        self.status_code = 404

class ExamNotFound(Exception):
    """in the case a non-existent client is being requested"""
    def __init__(self, examid, message = None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = f'The exam with id {examid}, does not exist. Please try again.'

        self.status_code = 404

class ContentNotFound(Exception):
    """in the case a non-existent resource is requested"""
    def __init__(self):
        Exception.__init__(self)
        
        self.message = ""
        
        self.status_code = 204


class MethodNotAllowed(Exception):
    """ Exception for the case a resource already exists in response to a POST request. """
    def __init__(self, *args, message=None, **kwargs):
        super().__init__(*args, **kwargs)
        if message:
            self.message = message
        else:
            self.message = 'The resource already exists. Use PUT to edit existing resources.'
        self.status_code = 405


class ClientDeniedAccess(Exception):
    """ Exception for the case a client denied access
        to a 3rd party resource in an OAuth request.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = 'Client denied access.'
        self.status_code = 409


class UnknownError(Exception):
    """ Exception for an unknown error. """
    def __init__(self, *args, message=None, **kwargs):
        super().__init__()
        if message:
            self.message = message
        else:
            self.message = 'Unknown error occured'
        self.status_code = 400

class InputError(Exception):
    """ Exception raised for errors with the input.

        Attributes:
        expression -- input expression in which the error occurred
        status_code -- Common status code for specific error
        message -- explanation of the error
    """
    def __init__(self, status_code, message):
        super().__init__()
        if message:
            self.message = message
        else:
            self.message = 'Input error'
        
        if status_code:
            self.status_code = status_code
        else:
            self.status_code = 400

class ContentNotFoundReturnData(Exception):
    """Special case for when a resource has not yet been created but the client must see other data to proceed"""
    def __init__(self, data=None, user_id = None):
        Exception.__init__(self)
        data.update({"user_id": user_id})
        self.status_code = 200
        self.message = "no instance of resource exists yet"

        self.data = data

class UnauthorizedUser(Exception):
    """in the case a staff member is trying to access resources they are not permitted to"""
    def __init__(self, email=None, message = None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = f'The staff member with email {email}, Is not authorized'

        self.status_code = 401


class ClientAlreadyExists(Exception):
    """in the case a staff member is trying to create a new client when the client already exists"""
    def __init__(self, identification=None, message = None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = f'The client identified by, {identification} already exists.'

        self.status_code = 409

class MedicalConditionNotFound(Exception):
    """Used if a medical condition is not found"""
    def __init__(self, medical_condition_id, message = None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = f'The medical condition with id, {medical_condition_id} does not exists.'

        self.status_code = 409

class MedicalConditionAlreadySubmitted(Exception):
    """Used if a medical condition is already submitted for a user"""
    def __init__(self,user_id, medical_condition_id, message = None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = f'The user, {user_id}, already submitted medical condition with id, {medical_condition_id}.'

        self.status_code = 409

class RelationAlreadyExists(Exception):
    """in the case a client is trying to be associated with a facility where this relationship is already defined"""
    def __init__(self, client_identification=None, facility_identification=None, message=None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = f'The client identified by, {client_identification} is already associated with the facility identified by {facility_identification}.'
        self.status_code = 409

class StaffEmailInUse(Exception):
    """in the case a staff member is creating a staff account with the same email"""
    def __init__(self, email, message = None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = f'The email, {email} is already in use for a staff account.'

        self.status_code = 409

class ClientEmailInUse(Exception):
    """in the case a staff member is creating a client account with the same email"""
    def __init__(self, email, message = None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = f'The email, {email} is already in use for a client account.'

        self.status_code = 409


class ClientNotFound(Exception):
    """in the case a staff member is trying to edit a client that does not exist"""
    def __init__(self, identification=None, message = None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = f'The client identified by, {identification} does not exit. Try another identification or create a new client.'

        self.status_code = 404

class TestNotFound(Exception):
    """in the case that blood test results are requested for a test id that does not exist"""
    def __init__(self, identification=None, message = None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = f'The blood test identified by, {identification} does not exit.'

        self.status_code = 404

class ResultTypeNotFound(Exception):
    """in the case that blood test result type is given where that result type does not exist"""
    def __init__(self, identification=None, message = None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = f'The blood test resultType identified by, {identification} does not exit.'

        self.status_code = 404

class FacilityNotFound(Exception):
    """in the case a staff member is trying to edit a client that does not exist"""
    def __init__(self, identification=None, message = None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = f'The facility identified by, {identification} does not exit. Try another identification or create a new registered facility.'

        self.status_code = 404

class IllegalSetting(Exception):
    """in the case an API request includes a setting or parameter that is not allowed"""
    def __init__(self, param=None, message = None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = f'Illegal Setting of parameter, {param}. You cannot set this value manually'

        self.status_code = 400

class InsufficientInputs(Exception):
    """in the case that the input does not have enough data"""
    def __init__(self, message = None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = 'Insufficient inputs supplied. At least 1 value other than date (and idx for PUT) must be given.'

        self.status_code = 405

class StaffNotFound(Exception):
    """in the case a non-existent staff member is being requested"""
    def __init__(self, user_id=None, message = None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = f'The Staff member with user_id {user_id}, does not exist. Please try again.'

        self.status_code = 404

class LoginNotAuthorized(Exception):
    """Used for auth.py if a user does not have certain authorizations
       for using the ModoBio APIs"""
    def __init__(self, message = None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = 'Not Authorized'

        self.status_code = 401

def bad_request(message):
    return error_response(400, message)

def error_response(status_code, message=None, data = None):
    response = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if data:
        response.update(data)
    if message:
        response['message'] = message
    response['status_code'] = status_code
    return response, status_code

@api.errorhandler(UserNotFound)
def error_user_does_not_exist(error):
    '''Return a custom message and 400 status code'''
    return error_response(error.status_code, error.message)

@api.errorhandler(ClientNotFound)
def error_client_not_found(error):
    '''Return a custom message and 400 status code'''
    return error_response(error.status_code, error.message)

@api.errorhandler(TestNotFound)
def error_test_not_found(error):
    '''Return a custom message and 400 status code'''
    return error_response(error.status_code, error.message)

@api.errorhandler(ExamNotFound)
def error_exam_not_found(error):
    '''Return a custom message and 400 status code'''
    return error_response(error.status_code, error.message)

@api.errorhandler(FacilityNotFound)
def error_exam_not_found(error):
    '''Return a custom message and 400 status code'''
    return error_response(error.status_code, error.message)

@api.errorhandler(ResultTypeNotFound)
def error_result_type_not_found(error):
    '''Return a custom message and 400 status code'''
    return error_response(error.status_code, error.message)

@api.errorhandler(ContentNotFound)
def error_content_not_found(error):
    '''Return a custom message and 204 status code'''
    return error_response(error.status_code, error.message)

@api.errorhandler(ContentNotFoundReturnData)
def error_content_not_found(error):
    '''Return a custom message with extra data in payload and 201 status code'''
    return error_response(error.status_code, error.message, error.data)

@api.errorhandler(MethodNotAllowed)
def error_method_not_allowed(error):
    """Return a custom message and 405 status code"""
    return error_response(error.status_code, error.message)

@api.errorhandler(ClientDeniedAccess)
def error_client_denied_access(error):
    """Return a custom message and 409 status code"""
    return error_response(error.status_code, error.message)

@api.errorhandler(UnknownError)
def error_unknown(error):
    """Return a custom message and 400 status code"""
    return error_response(error.status_code, error.message)

@api.errorhandler(InputError)
def error_input(error):
    """Return a custom message and status code"""
    return error_response(error.status_code, error.message)

@api.errorhandler(IllegalSetting)
def error_illegal_setting(error):
    '''Return a custom message and 400 status code'''
    return error_response(error.status_code, error.message)

@api.errorhandler(UnauthorizedUser)
def error_unauthorized_user(error):
    '''Return a custom message and 400 status code'''
    return error_response(error.status_code, error.message)

@api.errorhandler(ClientAlreadyExists)
def error_client_already_exists(error):
    '''Return a custom message and 409 status code'''
    return error_response(error.status_code, error.message)

@api.errorhandler(MedicalConditionNotFound)
def error_medical_condition_not_found(error):
    '''Return a custom message and 409 status code'''
    return error_response(error.status_code, error.message)    

@api.errorhandler(MedicalConditionAlreadySubmitted)
def error_medical_condition_already_submitted(error):
    '''Return a custom message and 409 status code'''
    return error_response(error.status_code, error.message)  

@api.errorhandler(RelationAlreadyExists)
def error_relation_already_exists(error):
    '''Return a custom message and 409 status code'''
    return error_response(error.status_code, error.message)

@api.errorhandler(StaffEmailInUse)
def error_staff_email_in_use(error):
    '''Return a custom message and 409 status code'''
    return error_response(error.status_code, error.message)

@api.errorhandler(ClientEmailInUse)
def error_client_email_in_use(error):
    '''Return a custom message and 409 status code'''
    return error_response(error.status_code, error.message)

@api.errorhandler(InsufficientInputs)
def error_insufficient_inputs(error):
    '''Return a custom message and 405 status code'''
    return error_response(error.status_code, error.message)

@api.errorhandler(StaffNotFound)
def error_staff_id_does_not_exist(error):
    '''Return a custom message and 400 status code'''
    return error_response(error.status_code, error.message)

@api.errorhandler(LoginNotAuthorized)
def error_login_not_authorized(error):
    '''Return a custom message and 400 status code'''
    return error_response(error.status_code, error.message)

def register_handlers(app):
    """register application-wide error handling"""
    @app.errorhandler(400)
    def default_error_handler(error):
        '''Default error handler'''
        return  error_response(getattr(error, 'code', 500), str(error)) 

    @app.errorhandler(Exception)
    def api_default_error_handler(error):
        '''Default error handler for api'''
        return  error_response(getattr(error, 'code', 500), str(error)) 
