from werkzeug.http import HTTP_STATUS_CODES

from odyssey.api import api


class UserNotFound(Exception):
    """in the case a non-existent client is being requested"""
    def __init__(self, clientid=None, message = None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = f'The client with clientid {clientid}, does not exist. Please try again.'

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


class ContentNotFoundReturnData(Exception):
    """Special case for when a resource has not yet been created but the client must see other data to proceed"""
    def __init__(self, data=None, clientid = None):
        Exception.__init__(self)
        data.update({"clientid": clientid})
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
    """in the case a staff member is creating a staff member with the same email"""
    def __init__(self, email, message = None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = f'The email, {email} is already in use.'

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

@api.errorhandler(ExamNotFound)
def error_exam_not_found(error):
    '''Return a custom message and 400 status code'''
    return error_response(error.status_code, error.message)

@api.errorhandler(FacilityNotFound)
def error_exam_not_found(error):
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

@api.errorhandler(RelationAlreadyExists)
def error_relation_already_exists(error):
    '''Return a custom message and 409 status code'''
    return error_response(error.status_code, error.message)

@api.errorhandler(StaffEmailInUse)
def error_staff_email_in_use(error):
    '''Return a custom message and 409 status code'''
    return error_response(error.status_code, error.message)

@api.errorhandler(InsufficientInputs)
def error_insufficient_inputs(error):
    '''Return a custom message and 405 status code'''
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
