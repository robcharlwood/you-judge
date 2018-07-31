import logging
import os

from djangae.settings_base import *
from django.core.urlresolvers import reverse_lazy

from core.boot import get_app_config

config = get_app_config()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# installed apps and middleware
INSTALLED_APPS = [
    'djangae',
    'django.contrib.contenttypes',
    'djangae.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.auth',
    'djangae.contrib.gauth_datastore',
    'djangae.contrib.security',
    'djangae.contrib.consistency',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    # you judge apps
    'accounts.app.AccountsConfig',
    'core.app.CoreConfig',
    'dashboard.app.DashboardConfig',
    'projects.app.ProjectsConfig',
    'services.app.ServicesConfig',
]

MIDDLEWARE = [
    'djangae.contrib.security.middleware.AppEngineSecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'djangae.contrib.gauth.middleware.AuthenticationMiddleware',
    'session_csrf.CsrfMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# project django settings
SECRET_KEY = config.secret_key
AUTH_USER_MODEL = 'accounts.User'
AUTHENTICATION_BACKENDS = [
    'accounts.backends.OauthenticationBackend',
]
ROOT_URLCONF = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'
ALLOWED_HOSTS = ['*']

# debug settings
DEBUG = True

# template settings
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': (
        os.path.join(BASE_DIR, '../templates'),
    ),
    'OPTIONS': {
        'context_processors': [
            'django.contrib.auth.context_processors.auth',
            'django.template.context_processors.debug',
            'django.template.context_processors.i18n',
            'django.template.context_processors.media',
            'django.template.context_processors.static',
            'django.template.context_processors.request',
            'django.template.context_processors.tz',
            'django.contrib.messages.context_processors.messages',
            'session_csrf.context_processor',
        ],
        'debug': True,
        'loaders': [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ],
    },
}]

# we're using a better version of django's default csrf middleware so
# we stop django warning us about it here.
SILENCED_SYSTEM_CHECKS = ['security.w003']


# internationalization and localization settings
LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# database and migration settings
MIGRATION_MODULES = {}

# date and number formatting
USE_THOUSAND_SEPARATOR = True

# logging settings
logging.getLogger().handlers[0].setFormatter(
    logging.Formatter('[%(module)s.%(funcName)s:%(lineno)s] %(message)s'))


LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_REDIRECT_SESSION_KEY = 'login_redirect_next_url'

# session csrf settings
ANON_ALWAYS = True

# use cookie based sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

# API Keys
YOUTUBE_API_KEY = config.youtube_api_key
CLOUD_NATURAL_LANG_API_KEY = config.cloud_nl_api_key

# Oauth2
GOOGLE_OAUTH2_CLIENT_ID = config.oauth2_client_id
GOOGLE_OAUTH2_CLIENT_SECRET = config.oauth2_client_secret
GOOGLE_OAUTH2_SCOPES = ['openid', 'email', 'profile']
GOOGLE_OAUTH2_FLOW_SESSION_KEY = 'oauth-flow'
GOOGLE_OAUTH2_REDIRECT_URI = reverse_lazy('oauth_step_two')
GOOGLE_OAUTH2_FLOWS = dict(
    default=dict(
        client_id=GOOGLE_OAUTH2_CLIENT_ID,
        client_secret=GOOGLE_OAUTH2_CLIENT_SECRET,
        scope=GOOGLE_OAUTH2_SCOPES,
        user_agent='you-judge-app',
        prompt='consent',
    )
)
