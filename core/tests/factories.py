import datetime

from django.contrib.auth import get_user_model
from django.utils import timezone

import factory
import pytz
from factory import fuzzy

from projects.models import Project
from videos.models import Video, VideoComment


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
    return timezone.now() + datetime.timedelta(days=10)


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


class ProjectFactory(factory.django.DjangoModelFactory):
    owner = factory.SubFactory(UserFactory)

    class Meta:
        model = Project


class VideoFactory(factory.django.DjangoModelFactory):
    project = factory.SubFactory(ProjectFactory)
    published = fuzzy.FuzzyDateTime(
        datetime.datetime(2017, 1, 1, tzinfo=pytz.UTC))

    class Meta:
        model = Video


class VideoCommentFactory(factory.django.DjangoModelFactory):
    video = factory.SubFactory(VideoFactory)
    published = fuzzy.FuzzyDateTime(
        datetime.datetime(2017, 1, 1, tzinfo=pytz.UTC))
    updated = fuzzy.FuzzyDateTime(
        datetime.datetime(2017, 1, 1, tzinfo=pytz.UTC))

    class Meta:
        model = VideoComment
