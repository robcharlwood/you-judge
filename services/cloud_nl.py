from googleapiclient import discovery

from django.conf import settings


class Client(object):
    """
    Wrapper around the cloud natural language API
    """
    def __init__(self, service=None):
        if service is None:
            service = discovery.build(
                'language', 'v1',
                developerKey=settings.CLOUD_NATURAL_LANG_API_KEY)
        self.service = service
