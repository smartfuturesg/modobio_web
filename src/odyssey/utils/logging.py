"""
This module handles logging for the API. It should be called before :class:`Flask` is instantiated.
"""

import logging
import time
from flask.json import dumps

# INFO = 20, CRITICAL = 30
audit_level = 25

def audit(self, msg, *args, **kwargs):
    """ Log a message with severity AUDIT.

    Use this logger to send messages to a special log
    which is filtered out and preserved for auditing.
    """
    logging.Logger.log(self, audit_level, msg, *args, **kwargs)

logging.Logger.audit = audit
logging.addLevelName(audit_level, 'AUDIT')
logging.captureWarnings(True)
logging.Formatter.converter = time.gmtime
logging.Formatter.default_msec_format = '%s.%03dZ'


class JsonFormatter(logging.Formatter):
    """ Format log messages as JSON. """

    def __init__(self):
        super().__init__(fmt='%(message)s')

    def usesTime(self) -> bool:
        """ Returns whether ``format()`` uses time.
        
        Returns
        -------
        bool
            Always returns ``True``.
        """
        return True

    def format(self, record: logging.LogRecord) -> str:
        """ Format :class:`logging.LogRecord` as a JSON string.

        Params
        ------
        record : :class:`logging.LogRecord`
            The LogRecord instance to be formatted.

        Returns
        -------
        str
            JSON formatted string of a dictionary with the following keys:
            - level: the name of the log level
            - numlevel: integer of the log level
            - name : name of the logger, equivalent to the package name where log was created
            - path: full path to the file in which log was created
            - line: line number in file `path` where log was created
            - timestamp: ISO 8601 formatted string, in UTC, of timestamp when log was created
            - message: the actual log message
            - error: traceback of error
            - trace: traceback of logger, only useful when debugging logging and error handling
        """
        error = ''
        if record.exc_info:
            error = self.formatException(record.exc_info)

        trace = ''
        if record.stack_info:
            trace = self.formatStack(record.stack_info)

        out = {
            'level': record.levelname,
            'numlevel': record.levelno,
            'name': record.name,
            'timestamp': self.formatTime(record, self.datefmt),
            'message': record.getMessage(),
            'path': record.pathname,
            'line': record.lineno,
            'error': error,
            'trace': trace}
        return dumps(out, separators=(',', ':'))
