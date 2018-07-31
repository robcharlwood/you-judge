import datetime
import json

from djangae.test import TestCase
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.utils import timezone

import mock
from oauth2client import client

from accounts.backends import OauthenticationBackend
from core.tests.factories import (
    AuthenticatedUserFactory,
    MockCredentials,
    UserFactory
)

MOCK_GET_PROFILE_RESPONSE = '''{
    "family_name": "van Rossum",
    "name": "Guido van Rossum",
    "picture": "https://lh3.googleusercontent.com/-4HX_UEt6nFk/AAAAAAAAAAI/AAAAAAAAAAA/Jv_VhtXa7hA/photo.jpg",
    "locale": "en-GB",
    "gender": "male",
    "email": "guido@python.org",
    "link": "https://plus.google.com/118000310282745873829",
    "given_name": "Guido",
    "id": "118000310282745873829",
    "hd": "python.org",
    "verified_email": true
}'''


class OauthenticationBackendTests(TestCase):
    def test_oauth_tokens_are_updated_on_each_login(self):
        """
        Test that when a user re-authenticates (i.e. logs back in) with our
        backend, that we update their User object with the new oauth tokens.
        """
        User = get_user_model()
        mock_userinfo = json.loads(MOCK_GET_PROFILE_RESPONSE)
        very_future = timezone.now() + timezone.timedelta(days=10)
        # Create a user who has logged in before, e.g one that has oauth tokens
        user = AuthenticatedUserFactory.create(
            email=mock_userinfo['email'],
            token_expiry=timezone.now() + timezone.timedelta(days=1))
        new_credentials = client.OAuth2Credentials(
            'my_token', 'my_client_id', 'my_client_secret', 'my_refresh_token',
            very_future, 'https://example.com/my/token/uri', 'my_user_agent')
        backend = OauthenticationBackend()
        with mock.patch(
                'accounts.backends.get_user_info', return_value=mock_userinfo):
            backend.authenticate(oauth_credentials=new_credentials)

        # Now check that the User object has been updated with the new creds
        user = User.objects.get(pk=user.pk)
        self.assertEqual(user.access_token, new_credentials.access_token)
        self.assertEqual(user.refresh_token, new_credentials.refresh_token)
        self.assertEqual(user.token_expiry, new_credentials.token_expiry)

    def test_no_credentials_returns_no_user(self):
        backend = OauthenticationBackend()
        self.assertIsNone(backend.authenticate(oauth_credentials=None))

    def test_failure_to_fetch_google_profile_returns_no_user(self):
        backend = OauthenticationBackend()
        with mock.patch('accounts.backends.get_user_info', return_value=None):
            self.assertIsNone(backend.authenticate(
                oauth_credentials=MockCredentials()))

    @override_settings(DJANGAE_CREATE_UNKNOWN_USER=True)
    def test_non_existent_user_is_created(self):
        user_info = dict(
            id='12345', email='1@example.com', given_name='Rob',
            family_name='Charlwood', name='Rob Charlwood')
        backend = OauthenticationBackend()
        with mock.patch(
                'accounts.backends.get_user_info', return_value=user_info):
            result = backend.authenticate(oauth_credentials=MockCredentials())
        self._check_user_info_values_match_user_fields(user_info, result)

        # It's a new user which (so far) is oauth-based only, so shouldn't
        # have a password
        self._check_has_unusable_password(result)

    def test_existing_user_is_returned_and_updated(self):
        """
        If there's an existing User with the same User ID as that of the
        fetched user profile, then the existing User should be returned but
        updated with latest profile info.
        """
        user = UserFactory.create(oauth_user_id='12345')
        user_info = dict(
            id='12345', email='1@example.com', given_name='Rob',
            family_name='Charlwood', name='Rob Charlwood')
        backend = OauthenticationBackend()
        with mock.patch(
                'accounts.backends.get_user_info', return_value=user_info):
            result = backend.authenticate(oauth_credentials=MockCredentials())
            self.assertEqual(result, user)

        # Now check that
        # (1) the returned user has been updated with the latest profile info
        # (2) User object in the DB has been updated with latest profile info
        user.refresh_from_db()
        for user_obj in result, user:
            self._check_user_info_values_match_user_fields(user_info, result)
            self._check_user_info_values_match_user_fields(user_info, user)

    def test_existing_token_missing_tz(self):
        user = UserFactory.create(oauth_user_id='12345')
        user_info = dict(
            id='12345', email='1@example.com', given_name='Rob',
            family_name='Charlwood', name='Rob Charlwood')
        backend = OauthenticationBackend()
        with mock.patch(
                'accounts.backends.get_user_info', return_value=user_info):
            result = backend.authenticate(oauth_credentials=MockCredentials(
                token_expiry=datetime.datetime.now()))
            self.assertEqual(result, user)

        # Now check that
        # (1) the returned user has been updated with the latest profile info
        # (2) User object in the DB has been updated with latest profile info
        user.refresh_from_db()
        for user_obj in result, user:
            self._check_user_info_values_match_user_fields(user_info, result)
            self._check_user_info_values_match_user_fields(user_info, user)

    def test_pre_created_user_is_matched_by_email(self):
        """
        If there's an existing User with the right email address but a username
        of None, then this is a pre-created User, which should be updated with
        the User ID and returned.
        """
        user = UserFactory.create(oauth_user_id=None, email='1@example.com')
        user_info = dict(
            id='12345', email='1@example.com', given_name='Rob',
            family_name='Charlwood', name='Rob Charlwood')
        backend = OauthenticationBackend()
        with mock.patch(
                'accounts.backends.get_user_info', return_value=user_info):
            result = backend.authenticate(oauth_credentials=MockCredentials())

        # It should have used the existing user but updated it with the new
        # profile values
        self.assertEqual(result, user)

        # Now check that
        # (1) the returned user has been updated with the latest profile info
        # (2) User object in the DB has been updated with latest profile info
        user.refresh_from_db()
        for user_obj in result, user:
            self._check_user_info_values_match_user_fields(user_info, result)
            self._check_user_info_values_match_user_fields(user_info, user)

    def test_conflicting_user_with_same_email_is_not_reused(self):
        """
        If there's an existing User with the right email address but a
        different oauth_user_id, then the existing user should have its email
        field wiped (because it's unqiue) and a new user should be created
        and returned.
        """
        user = UserFactory.create(oauth_user_id='9999', email='1@example.com')
        user_info = dict(
            id='12345', email='1@example.com', given_name='Rob',
            family_name='Charlwood', name='Rob Charlwood')
        backend = OauthenticationBackend()
        with mock.patch(
                'accounts.backends.get_user_info', return_value=user_info):
            result = backend.authenticate(oauth_credentials=MockCredentials())

        # It should have created a new user
        self.assertNotEqual(result, user)
        self.assertEqual(get_user_model().objects.count(), 2)

        # The existing user should now have a blank 'email' field
        user.refresh_from_db()
        self.assertEqual(user.email, '')

        # We should get a new user object with correct email & oauth_user_id
        self._check_user_info_values_match_user_fields(user_info, result)

        # And because it created a new user via oauth, it shouldn't have a
        # usable password
        self._check_has_unusable_password(result)

    def test_user_info_without_values_saves_empty_strings(self):
        """
        If user_info does not contain given_name, first_name, family_name,
        instead of erroring we save empty strings and continue.
        """
        user_info = dict(id='12345', email='1@example.com')
        EMPTY_VALUE = ''
        EMPTY_FIELDS = ['first_name', 'last_name', 'full_name']
        backend = OauthenticationBackend()
        with mock.patch(
                'accounts.backends.get_user_info', return_value=user_info):
            result = backend.authenticate(oauth_credentials=MockCredentials())
        for field in EMPTY_FIELDS:
            self.assertEqual(getattr(result, field), EMPTY_VALUE)

    @override_settings(DJANGAE_CREATE_UNKNOWN_USER=False)
    def test_create_unknown_user_setting_respected(self):
        User = get_user_model()
        user_info = dict(
            id='12345', email='1@example.com', given_name='Rob',
            family_name='Charlwood', name='Rob Charlwood')
        backend = OauthenticationBackend()
        with mock.patch(
                'accounts.backends.get_user_info', return_value=user_info):
            result = backend.authenticate(oauth_credentials=MockCredentials())
        self.assertEqual(result, None)
        self.assertEqual(User.objects.count(), 0)

    def _check_user_info_values_match_user_fields(self, user_info, user):
        """
        Given a user_info dict and User object, check that the values match up.
        """
        mapping = dict(
            id='oauth_user_id',
            email='email',
            given_name='first_name',
            family_name='last_name',
            name='full_name',
        )
        for key, field in mapping.items():
            if user_info[key] != getattr(user, field):
                self.fail("user_info[%r] (%r) did not match User.%s (%r)" % (
                    key, user_info[key], field, getattr(user, field)
                ))

    def _check_has_unusable_password(self, user):
        """
        A normal password hash is in the format
        "hasher_name$num_rounds$hash_value". An unusable password is in the
        format "!things"
        """
        self.assertTrue(
            user.password.startswith("!") and "$" not in user.password)
