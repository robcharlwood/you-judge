from djangae.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

import mock

from accounts.models import User
from core.tests.factories import MockCredentials, UserFactory, days_ahead


class UserTest(TestCase):
    def test_unicode(self):
        user = UserFactory.create(
            full_name="John Smith", email="j.smith@test.com")
        self.assertEquals(unicode(user), "j.smith@test.com")

    def test_default_model(self):
        """Test that Django is using our model"""
        self.assertEquals(User, get_user_model())

    def test_reset_tokens(self):
        user_with_tokens = UserFactory.create(
            username='1', email='1@example.com', access_token='1',
            refresh_token='2', token_expiry=timezone.now())
        user_with_tokens.reset_tokens()
        user_with_tokens.refresh_from_db()
        self.assertEquals('', user_with_tokens.access_token)
        self.assertEquals('', user_with_tokens.refresh_token)

    def test_is_authenticated(self):
        """ Test our custom User.is_authenticated property. """

        # create past and future dates
        past = timezone.now() - timezone.timedelta(days=1)
        future = timezone.now() + timezone.timedelta(days=1)

        # create some users
        user_with_tokens = UserFactory.create(
            username='1', email='1@example.com', access_token='1',
            refresh_token='2', token_expiry=future)
        user_with_expired_tokens = UserFactory.create(
            username='2', email='2@example.com', access_token='1',
            refresh_token='2', token_expiry=past)
        user_without_tokens = UserFactory.create(
            username='3', email='3@example.com', access_token='',
            refresh_token='2', token_expiry=future)
        user_without_refresh_token = UserFactory.create(
            username='4', email='4@example.com', access_token='1',
            refresh_token='', token_expiry=future)

        # check authenticated status for each user
        self.assertTrue(user_with_tokens.is_authenticated)
        self.assertFalse(user_with_expired_tokens.is_authenticated)
        self.assertFalse(user_without_tokens.is_authenticated)
        self.assertFalse(user_without_refresh_token.is_authenticated)

    def test_is_authenticated_refresh_required(self):
        """ Test our custom User.is_authenticated property. """

        # create past
        past = timezone.now() - timezone.timedelta(days=1)

        # create a user who token has expired
        user_with_tokens = UserFactory.create(
            username='1', email='1@example.com', access_token='1',
            refresh_token='2', token_expiry=past)

        # adding this because of random No route to host errors
        with mock.patch(
                'accounts.models.OAuth2Credentials') as mock_oauth:
            mock_oauth.return_value = MockCredentials(access_token='foo')
            self.assertTrue(user_with_tokens.is_authenticated)

    def test_invalid_oauth_tokens(self):
        invalid_cases = (
            dict(access_token='', refresh_token='', token_expiry=''),
            dict(access_token='foo', refresh_token='', token_expiry=''),
            dict(access_token='', refresh_token='bar', token_expiry=''),
            dict(access_token='foo', refresh_token='bar', token_expiry=''),
            dict(
                access_token='', refresh_token='bar',
                token_expiry=days_ahead(1)),
            dict(
                access_token='foo', refresh_token='',
                token_expiry=days_ahead(1)),
            dict(
                access_token='foo', refresh_token='bar',
                token_expiry=timezone.now() - timezone.timedelta(days=1)),
        )
        for invalid_case in invalid_cases:
            self.assertEqual(
                UserFactory.build(**invalid_case)._oauth_tokens_are_valid(),
                False
            )

    def test_valid_oauth_tokens(self):
        self.assertTrue(
            UserFactory.build(
                access_token='foo', refresh_token='bar',
                token_expiry=timezone.now() + timezone.timedelta(days=1)
            )._oauth_tokens_are_valid(),
            True
        )

    def test_oauth_tokens_are_valid_empty_access(self):
        self.assertEqual(
            UserFactory.build(
                access_token='', refresh_token='', token_expiry=''
            )._oauth_tokens_are_valid(),
            False
        )
