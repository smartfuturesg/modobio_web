
from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

from odyssey import app
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

@app.errorhandler(400)
def default_error_handler(error):
    '''Default error handler'''
    return  error_response(getattr(error, 'code', 500), str(error)) 

@app.errorhandler(Exception)
def api_default_error_handler(error):
    '''Default error handler for api'''
    return  error_response(getattr(error, 'code', 500), str(error)) 

