import json
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import BaseUserManager
from django.db.utils import IntegrityError
from django.utils import timezone

import httplib2
import pytz
from oauth2client import client


class OauthenticationBackend(ModelBackend):
    def authenticate(self, oauth_credentials=None):
        """
        Handles authentication of a user from the given
        oauth2client.OAuth2Credentials object. User objects are keyed by the
        Google User ID, which is stored in the oauth_user_id field.
        """
        if oauth_credentials is None:
            return None

        User = get_user_model()
        user_info = get_user_info(oauth_credentials)
        if not user_info:
            return None

        user_id = user_info['id']
        email = BaseUserManager.normalize_email(user_info['email'])
        try:
            user = User.objects.get(oauth_user_id=user_id)
        except User.DoesNotExist:
            pass
        else:
            # Update the existing User object with the new oauth tokens and
            # any user_info changes
            values = get_user_values_to_store(
                oauth_credentials, user_info, creating=False)
            for field, value in values.items():
                setattr(user, field, value)
            user.save()
            return user

        # honour djangae's create unknown user setting
        if not getattr(settings, 'DJANGAE_CREATE_UNKNOWN_USER', True):
            return None

        # OK. We will grant access. We may need to update an existing user, or
        # create a new one, or both.
        # Those 3 scenarios are:
        # 1. A User object has been created for this user, but they have not
        # logged in yet. In this case we fetch the User object by email,
        # and then update it with the Google User ID
        # 2. A User object exists for this email address but belonging to a
        # different Google account. This generally only happens when the email
        # address of a Google Apps account has been signed up as a Google
        # account and then the apps account itself has actually become a
        # Google account. This is possible but very unlikely.
        # 3. There is no User object relating to this user whatsoever.
        user_values = get_user_values_to_store(oauth_credentials, user_info)
        try:
            existing_user = User.objects.get(email=email)
        except User.DoesNotExist:
            existing_user = None
        if existing_user:
            if existing_user.oauth_user_id is None:
                # The user has been pre-created in the datastore
                # (but the person hasn't yet logged in).
                # We can use the existing user for this new login.
                existing_user.oauth_user_id = user_id
                existing_user.email = email
                for field_name, value in user_values.items():
                    setattr(existing_user, field_name, value)
                existing_user.save()
                return existing_user
            else:
                # We need to wipe out the email on the existing user and
                # create a new one.
                User.objects.filter(pk=existing_user.pk).update(
                    email='', email_lower=None)
                return User.objects.create(
                    username=None, oauth_user_id=user_id,
                    password=make_password(None), **user_values)
        else:
            # Create a new user, but account for another thread having created
            # it already in a race condition scenario.
            try:
                return User.objects.create(
                    username=None, oauth_user_id=user_id,
                    password=make_password(None), **user_values)
            except IntegrityError:  # pragma: no cover
                # We just return this without updating it, because if we're
                # here then we're in a race condition scenario, so it should
                # have been very recently created/updated
                return User.objects.get(oauth_user_id=user_id)


def get_user_info(credentials):  # pragma: no cover
    """
    Given an oauth2client.OAuth2Credentials object, make a request to Google
    auth land to get the profile info for the auth'd user.
    """
    try:
        http = httplib2.Http()
        http = credentials.authorize(http)
        response = http.request(
            'https://www.googleapis.com/oauth2/v2/userinfo')
    except client.Error:
        logging.exception(
            "Oauth error trying to get user's profile info from Google")
        return None
    user_info = json.loads(response[1])
    return user_info


def get_user_values_to_store(credentials, user_info, creating=True):
    """
    Given an oauth2client.OAuth2Credentials object and the user_info dict
    returned from get_user_info() for that user, return a dict of field values
    that we want to save onto the User object.
    """
    token_expiry = credentials.token_expiry
    if not token_expiry.tzinfo:
        token_expiry = pytz.timezone(settings.TIME_ZONE).localize(
            credentials.token_expiry)
    values = dict(
        email=BaseUserManager.normalize_email(user_info['email']),
        first_name=user_info.get('given_name', ''),
        last_name=user_info.get('family_name', ''),
        full_name=user_info.get('name', ''),
        profile_image_url=user_info.get('picture', ''),
        last_login=timezone.now(),
        access_token=credentials.access_token,
        refresh_token=credentials.refresh_token,
        token_expiry=token_expiry)
    return values
