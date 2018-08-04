from django.conf import settings

from googleapiclient import discovery


class Client(object):
    """
    Wrapper around the cloud natural language API
    """
    def __init__(self, service=None):
        if service is None:  # pragma: no cover
            service = discovery.build(
                'language', 'v1',
                developerKey=settings.CLOUD_NATURAL_LANG_API_KEY)
        self.service = service

    def analyze_sentiment(self, text, lang='en', ctype='PLAIN_TEXT'):
        """
        Takes a string and performs setiment anaylsis on it using google's
        cloud service
        """
        results = self.service.documents().analyzeSentiment(body={
            'document': {
                'language': lang,
                'content': text,
                'type': ctype,
            }
        }).execute()
        return results
