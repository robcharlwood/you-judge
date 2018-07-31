import logging
import random
import time

from djangae.db import transaction

from google.appengine.api.datastore_errors import \
    TransactionFailedError as AppEngineTransactionFailedError


def do_with_retry(func, *args, **kwargs):
    """
    Tries a function 3 times using exponential backoff according to Google
    API specs.  Optional kwargs:
        `_attempts` - override the number of attempts before giving up.
        `_catch` - tuple of exception types used in `except types as e`.
    """
    MINIMUM_WAIT = 0.5
    _catch = kwargs.pop("_catch", (
        transaction.TransactionFailedError, AppEngineTransactionFailedError))
    _attempts = kwargs.pop('_attempts', 3)

    for n in xrange(_attempts):
        try:
            return func(*args, **kwargs)
        except _catch, e:  # pragma: no cover
            # back off by factor of two plus a random number of milliseconds
            # to prevent deadlocks (according to API docs..)
            logging.warning("Transient error ({}), retrying...".format(e))
            time.sleep(MINIMUM_WAIT + (
                2 ** n + float(random.randint(0, 1000)) / 1000))
    else:  # pragma: no cover
        raise
