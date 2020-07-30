from werkzeug.http import HTTP_STATUS_CODES

from odyssey.api import api


class UserNotFound(Exception):
    """in the case a non-existent client is being requested"""
    def __init__(self, clientid, message = None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = f'The client with clientid {clientid}, does not exist. Please try again.'

        self.status_code = 404

class ContentNotFound(Exception):
    """in the case a non-existent resource is requested"""
    def __init__(self):
        Exception.__init__(self)
        
        self.message = ""
        
        self.status_code = 204

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


class ClientNotFound(Exception):
    """in the case a staff member is trying to edit a client that does not exist"""
    def __init__(self, identification=None, message = None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = f'The client identified by, {identification} does not exit. Try another identification or create a new client.'

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


def bad_request(message):
    return error_response(400, message)

def error_response(status_code, message=None):
    response = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
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

@api.errorhandler(ContentNotFound)
def error_content_not_found(error):
    '''Return a custom message and 204 status code'''
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
