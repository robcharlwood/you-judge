from googleapiclient import discovery

from django.conf import settings


class Client(object):
    """
    Wrapper around the YouTube data API
    """
    def __init__(self, service=None):
        if service is None:
            service = discovery.build(
                'youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
        self.service = service
