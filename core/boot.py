import sys
from os.path import abspath, dirname, exists, join

PROJECT_DIR = dirname(dirname(abspath(__file__)))
SITEPACKAGES_DIR = join(PROJECT_DIR, "sitepackages")
DEV_SITEPACKAGES_DIR = join(SITEPACKAGES_DIR, "dev")
PROD_SITEPACKAGES_DIR = join(SITEPACKAGES_DIR, "prod")
APPENGINE_DIR = join(DEV_SITEPACKAGES_DIR, "google_appengine")


def fix_path(include_dev_libs=False):
    """
    Insert libs folder(s) and SDK into sys.path. The one(s) inserted
    last take priority.
    """
    if include_dev_libs:
        if exists(APPENGINE_DIR) and APPENGINE_DIR not in sys.path:
            sys.path.insert(1, APPENGINE_DIR)

        if DEV_SITEPACKAGES_DIR not in sys.path:
            sys.path.insert(1, DEV_SITEPACKAGES_DIR)

    from google.appengine.ext import vendor
    vendor.add(PROD_SITEPACKAGES_DIR)


def get_app_config():
    """
    Returns the application configuration, creating it if necessary.
    """
    from django.utils.crypto import get_random_string
    from google.appengine.ext import ndb

    class Config(ndb.Model):
        """
        A simple key-value store for application configuration settings.
        """
        secret_key = ndb.StringProperty()
        youtube_api_key = ndb.StringProperty()

    # set a random bunch of chars that we can create a secret key from
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'

    @ndb.transactional()
    def txn():
        # Get or create the Config in a transaction, so that if it doesn't
        # exist we don't get 2 threads creating a Config object and one
        # overwriting the other
        key = ndb.Key(Config, 'config')
        entity = key.get()
        if not entity:
            entity = Config(key=key)
            entity.secret_key = get_random_string(50, chars)
            entity.youtube_api_key = 'Update me with your YouTube API Key!'
            entity.put()
        return entity
    return txn()
