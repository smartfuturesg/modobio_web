import logging

import celery
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout
from werkzeug.exceptions import BadRequest

logger = logging.getLogger(__name__)

class BaseTaskWithRetry(celery.Task):
    """ Base class for celery tasks which defines rules for autoretries.

    Retries will automatically occur for the exceptions listed in the
    ``autoretry_for`` attribute.
    """
    autoretry_for = (Exception,)
    max_retries = 5
    retry_backoff = True
    retry_backoff_max = 700
    retry_jitter = True

class IntegrationsBaseTaskWithRetry(celery.Task):
    """ Base class for celery tasks that rely on external integrations.

    Retries will automatically occur for the exceptions listed in the
    ``autoretry_for`` attribute.
    """
    # HTTPError will only include 4xx errors and should not be retried
    # see request handler in integrations/active_campaign.py
    autoretry_for = (BadRequest, ConnectionError, Timeout)
    throws = (HTTPError, BadRequest, ConnectionError, Timeout)
    max_retries = 5
    retry_backoff = True
    retry_backoff_max = 700
    retry_jitter = True
