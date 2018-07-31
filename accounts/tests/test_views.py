from djangae.test import TestCase
from django.conf import settings
from django.test import RequestFactory

import mock
from oauth2client import client

from accounts.views import OauthStepOne, OauthStepTwo
from core.tests.factories import MockCredentials, UserFactory

mock_step_one = 'accounts.views.client.OAuth2WebServerFlow.step1_get_authorize_url'
mock_step_two = 'accounts.views.client.OAuth2WebServerFlow.step2_exchange'


class OAuthViewsTests(TestCase):
    def test_step_one(self):
        factory = RequestFactory()
        request = factory.get('/')
        request.session = {}

        with mock.patch(mock_step_one, return_value="/some/url/"):
            response = OauthStepOne.as_view()(request)
            self.assertEquals(response['Location'], "/some/url/")

    def test_step_one_next_url(self):
        factory = RequestFactory()
        request = factory.get('/', {'next': '/foo/bar/'})
        request.session = {}

        with mock.patch(mock_step_one, return_value="/some/url/"):
            response = OauthStepOne.as_view()(request)
            self.assertEqual(
                request.session['login_redirect_next_url'], '/foo/bar/')
            self.assertEquals(response['Location'], "/some/url/")

    def test_step_two_logs_user_in(self):
        factory = RequestFactory()
        request = factory.get('/')
        request.session = {}
        user = UserFactory.create()

        with mock.patch(mock_step_two, return_value=MockCredentials()):
            with mock.patch(
                'accounts.views.auth.authenticate', return_value=user
                    ) as authenticate:
                with mock.patch('accounts.views.auth.login') as login_mock:
                    response = OauthStepTwo.as_view()(request)

        self.assertTrue(authenticate.called)
        self.assertTrue(login_mock.called)

        # And we expect it to redirect us on to the dashboard view
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], settings.LOGIN_REDIRECT_URL)

    def test_step_two_raises_flow_exchange_error(self):
        factory = RequestFactory()
        request = factory.get('/')
        request.session = {}

        with mock.patch(
            'accounts.views.client.OAuth2WebServerFlow.step2_exchange',
                side_effect=client.FlowExchangeError):
            with mock.patch('accounts.views.messages.error') as messages_error:
                with mock.patch('accounts.views.auth.login') as auth_login:
                    try:
                        response = OauthStepTwo.as_view()(request)
                        self.assertEqual(response.status_code, 302)
                        self.assertFalse(auth_login.called)
                        self.assertTrue(messages_error.called)
                        self.assertEqual(
                            messages_error.call_args[0][1],
                            'Try connecting your account again.'
                        )
                    except client.FlowExchangeError:
                        self.fail('Raised an exception; should be handled.')

    def test_step_two_log_in_fails(self):
        factory = RequestFactory()
        request = factory.get('/')
        request.session = {}
        user = UserFactory.create()

        with mock.patch('accounts.views.messages.error') as messages_error:
            with mock.patch(mock_step_two, return_value=MockCredentials()):
                with mock.patch(
                    'accounts.views.auth.authenticate', return_value=user
                        ) as authenticate:
                    with mock.patch('accounts.views.auth.login') as login_mock:
                        authenticate.return_value = None
                        response = OauthStepTwo.as_view()(request)

        self.assertTrue(authenticate.called)
        self.assertTrue(messages_error.called)
        self.assertFalse(login_mock.called)
        self.assertEqual(
            messages_error.call_args[0][1],
            'Try connecting your account again.'
        )

        # And we expect it to redirect us on to the login view
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], settings.LOGIN_URL)
