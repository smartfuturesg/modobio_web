import celery


class BaseTaskWithRetry(celery.Task):
    """
    Base class for celery tasks which defines rules for autoretries

    Retries will automatically occur for the exceptions listen in the `autoretry_for` attribute
    """
    autoretry_for = (Exception,)
    max_retries = 5
    retry_backoff = True
    retry_backoff_max = 700
    retry_jitter = True