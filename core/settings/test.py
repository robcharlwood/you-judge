import os

from .base import *

INSTALLED_APPS = INSTALLED_APPS + ['django_nose']

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--cover-package=accounts',
    '--cover-package=core',
    '--cover-package=dashboard',
    '--cover-package=moments',
    '--cover-package=services',
    '--with-progressive',
    '--logging-level=CRITICAL',
    '--logging-clear-handlers',
    '-s'
]

NOSE_PLUGINS = [
    'nose_exclude.NoseExclude',
    'djangae.noseplugin.DjangaePlugin',
]

DEBUG = False

DJANGAE_CACHE_ENABLED = False

# needed for the djangae tests
os.environ['DEFAULT_VERSION_HOSTNAME'] = '{}:{}'.format(
    os.environ['SERVER_NAME'], os.environ['SERVER_PORT'])
