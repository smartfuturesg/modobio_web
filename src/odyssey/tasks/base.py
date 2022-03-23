import logging

import celery

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
