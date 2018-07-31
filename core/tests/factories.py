from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

import factory


class MockCredentials(object):
    """
    Mocks authenticated Oauth2 credentials.
    """
    def __init__(self, **kwargs):
        defaults = dict(
            access_token='access',
            refresh_token='refresh',
            token_expiry=timezone.now() + timezone.timedelta(days=1))
        defaults.update(**kwargs)
        for attr, value in defaults.items():
            setattr(self, attr, value)

    def refresh(self, http):
        return None


def token_expiry():
    """
    Mocks a tokens expiry
    """
    return timezone.now() + timedelta(days=10)


def days_ahead(days):
    """
    Mocks a certain number of days ahead
    """
    return timezone.now() + timezone.timedelta(days=days)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()


class AuthenticatedUserFactory(UserFactory):
    refresh_token = True
    access_token = True
    token_expiry = factory.LazyFunction(token_expiry)
