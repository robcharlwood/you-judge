import xml.etree.ElementTree as ElementTree

from django.conf import settings

from googleapiclient import discovery
from lxml import html
from lxml.html.clean import clean_html
from pytube import YouTube
from pytube.compat import unescape


class Client(object):
    """
    Wrapper around the YouTube data API
    """
    def __init__(self, service=None):
        if service is None:
            service = discovery.build(
                'youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
        self.service = service

    def search(self, query, part="id,snippet", max_results=50):
        """
        Searches YouTube based on the passed data
        """
        results = self.service.search().list(
            q=query,
            part=part,
            maxResults=max_results,
            type="video"
        ).execute()
        return results.get('items', [])

    def get_video_comments(self, video_id, max_results=100, order="relevance"):
        """
        Retrieves comments for a video
        """
        results = self.service.commentThreads().list(
            part="snippet",
            videoId=video_id,
            textFormat="html",
            maxResults=max_results,
            order=order,
        ).execute()
        return results.get('items', [])

    def get_video_transcript(self, video_id):
        """
        Retrieves and formats transcripts for the passed video

        TODO: If no captions are available, download audio track and pass into
        Cloud Speech-to-Text? for now we just return None implying that we cant
        perform sentiment analysis on the video content itself.
        """
        video = YouTube('https://www.youtube.com/watch?v={}'.format(video_id))
        captions = video.captions.get_by_language_code('en')
        if not captions:
            return

        # format captions as plaintext and strip trailing whitespace and html
        captions = ElementTree.fromstring(captions.xml_captions)
        captions_list = []
        for subtitle in captions.getchildren():
            text = subtitle.text or u''
            caption = unescape(text.replace('\n', ' ').replace('  ', ' '))
            captions_list.append(u"{text} ".format(text=caption))
        transcript = clean_html(
            html.fromstring(u''.join(captions_list).strip()))
        return transcript.text_content().strip()
