import logging
import traceback

from flask import current_app
from werkzeug.exceptions import HTTPException
from werkzeug.http import HTTP_STATUS_CODES

from odyssey.api import api

logger = logging.getLogger(__name__)


@api.errorhandler(HTTPException)
def http_exception_handler(error: HTTPException) -> tuple:
    """ Create a JSON response from any HTTPException.

    :class:`werkzeug.exceptions.HTTPException`s are handled by default by flask-restx,
    but this handler adds extra information to the error response. It also logs the
    error, including the error traceback. It is logged at the :attr:`logging.INFO` level,
    because it is a handled error, i.e. the message is forwarded to the user.

    This handles :class:`werkzeug.exceptions.HTTPException`s and **all it's subclasses**.

    Traceback information is added to the response for ``DEV`` and ``TESTING`` environments.
    It is **not** added in the production environment, for security reasons. It is
    available under the ``trace`` keyword in the response. In all three environments,
    the same traceback information is added to logs.

    It is possible to add custom values to the error response. Add a ``.data`` attribute
    to the error, which holds a dictionary.::

        err = BadRequest('Something happened.')
        err.data = {'extra': 'output'}
        raise err

        # Returns:
        {"error": "Bad request",
         "message": "Something happened",
         "status_code": 400,
         "extra": "output",
         "trace": ["File ..., line x:", "..."]}

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
    # Keep this order so that custom values from error.data can be added to the
    # response, but cannot be used to override status_code, message, and error.
    response = {}
    if hasattr(error, 'data') and isinstance(error.data, dict):
        response = error.data

    response['status_code'] = error.code
    response['message'] = error.description
    response['error'] = HTTP_STATUS_CODES.get(error.code, 'Unknown error')

    # Full traceback for testing and dev only.
    if current_app.config['TESTING']:
        tb = traceback.format_tb(error.__traceback__)
        response['trace'] = ''.join(tb)
    elif current_app.config['DEV']:
        tb = []
        # This looks better in swagger
        for line in traceback.format_tb(error.__traceback__):
            tb.extend(line.strip('\n').split('\n'))
        response['trace'] = tb

    logger.info(error.description, exc_info=True)

    return response, error.code

@api.errorhandler(Exception)
def exception_handler(error):
    """ Create a JSON response from any :class:`Exception` that is not handled by :func:`http_exception_handler`.

    Flask usually turns any unhandled :class:`Exception` into a
    :class:`werkzeug.exceptions.InternalServerError`, but does not provide any further
    information as to where the exception was raised. This is done for security: we do
    not want to provide any extra information about the inner workings of out program
    which may be exploited.

    This handler returns a 500 (Internal server error) as expected, but also logs the
    error with a traceback. It is logged at :attr:`logging.ERROR` level, because this
    is an unhandled error, i.e. something unexpected went wrong in the background and
    the user does not need to be informed what that is.

    When running in ``TESTING`` mode (pytest) the original error is re-raised, without
    wrapping it in a :class:`werkzeug.exceptions.InternalServerError`. That gives
    a full traceback in pytest, which makes it easier for developers to trace the
    error back to the code.

    In ``DEV`` mode, traceback information is added to the response. It is **not**
    added in the production environment, for security reasons. It is available under
    the ``trace`` keyword in the response.

    This handles :class:`Exception`s and **all it's subclasses** that are not otherwise
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
    # Simply reraise the error in testing, gives an immediate and clear traceback.
    if current_app.config['TESTING']:
        raise error

    # Keep this order so that custom values from error.data can be added to the
    # response, but cannot be used to override status_code, message, and error.
    response = {}
    if hasattr(error, 'data') and isinstance(error.data, dict):
        response = error.data

    response['status_code'] = 500
    response['error'] = 'Internal server error'
    response['message'] = 'Internal server error'

    if current_app.config['DEV']:
        tb = []
        # This looks better in swagger
        for line in traceback.format_tb(error.__traceback__):
            tb.extend(line.strip('\n').split('\n'))
        response['trace'] = tb + [repr(error)]

    # Why is this logger twice?
    # logger.error(repr(error), exc_info=True)

    return response, 500
