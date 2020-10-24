from werkzeug.http import HTTP_STATUS_CODES
from odyssey.api import api
from odyssey.errors import handlers

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
