import logging

from djangae.contrib.gauth_datastore.models import GaeAbstractDatastoreUser
from djangae.contrib.locking import lock
from djangae.db import transaction
from django.conf import settings
from django.db import models
from django.utils import timezone

import httplib2
import pytz
from oauth2client.client import AccessTokenRefreshError, OAuth2Credentials

from .utils import do_with_retry


class CharOrNoneField(models.CharField):
    """
    Custom model field that if a field is not passed a value, it will be
    stored to the datastore as None
    """
    empty_strings_allowed = False

    def pre_save(self, model_instance, add):
        value = super(CharOrNoneField, self).pre_save(model_instance, add)
        if not value:
            return None
        return value


class User(GaeAbstractDatastoreUser):
    """
    User model - to track and store user data
    """
    full_name = models.CharField(max_length=200, null=True)
    oauth_user_id = CharOrNoneField(
        max_length=50, blank=True, null=True, unique=True, default=None)
    access_token = models.CharField(max_length=200, blank=True)
    refresh_token = models.CharField(max_length=200, blank=True)
    token_expiry = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return u'{}'.format(self.email)

    def refresh_tokens(self):
        """
        Refreshes self.access_token and updates self.token_expiry.
        Returns True if refresh was successful, False otherwise.
        """
        lock_id = "refresh_tokens:%s" % self.pk
        with lock(lock_id, steal_after_ms=6000):
            self.refresh_from_db()
            if self._oauth_tokens_are_valid():  # pragma: no cover
                return
            credentials = OAuth2Credentials(
                self.access_token,
                settings.GOOGLE_OAUTH2_CLIENT_ID,
                settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                self.refresh_token,
                self.token_expiry,
                'https://accounts.google.com/o/oauth2/token',
                'YouJudge Client')

            # Do a refresh - this should update access_token and token_expiry
            try:
                credentials.refresh(httplib2.Http(proxy_info=None, timeout=5))
            except AccessTokenRefreshError as e:
                logging.error(
                    "Couldn't refresh oauth tokens for user {}. "
                    "Error was {}".format(self, e))
                return
            with transaction.atomic():
                self.refresh_from_db()
                if credentials.access_token != self.access_token:
                    self.access_token = credentials.access_token
                    self.token_expiry = credentials.token_expiry.replace(
                        tzinfo=pytz.UTC)
                    self.save()

    def _oauth_tokens_are_valid(self):
        """
        Helper method to check whether user tokens are valid
        """
        return (
            bool(self.access_token) and
            bool(self.refresh_token) and
            bool(self.token_expiry) and
            self.token_expiry > timezone.now()
        )

    def reset_tokens(self):
        self.access_token = ''
        self.refresh_token = ''
        self.save(update_fields=['access_token', 'refresh_token'])

    @property
    def is_authenticated(self):
        """
        Even if the user is authenticated, we still want to trigger
        re-authentication if their oauth tokens have expired or been wiped out.
        """
        if self._oauth_tokens_are_valid():
            return True

        if not self.refresh_token:
            return False

        # refresh user token
        try:
            do_with_retry(
                self.refresh_tokens, _catch=transaction.TransactionFailedError)
        except transaction.TransactionFailedError:  # pragma: no cover
            logging.error(
                "User.is_authenticated couldn't update tokens for UserID:{} "
                "due to contention".format(self.id))
            return False
        return self._oauth_tokens_are_valid()
