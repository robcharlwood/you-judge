# -*- coding: utf-8 -*-
from djangae.test import TestCase

import mock

from services.youtube import Client

MOCK_CAPTIONS_XML = u"""<?xml version="1.0" encoding="utf-8" ?>
<transcript>
    <text start="4.75" dur="5.12">Hello world!</text>
    <text start="11.77" dur="7.549">Im Rob Charlwood and Im an Engineer</text>
</transcript>
"""

MOCK_CAPTIONS_XML_UTF8 = u"""<?xml version="1.0" encoding="utf-8" ?>
<transcript>
    <text start="4.75" dur="5.12">象は鼻が長</text>
    <text start="11.77" dur="7.549">I\u2019m Rob Charlwood - Engineer</text>
</transcript>
"""


class YouTubeClientTestCase(TestCase):
    def test_search(self):
        expected_items = [{
            u'etag': u'"etag/123456789"',
            u'id': u'video1234',
            u'kind': u'youtube#video',
            u'snippet': {
                u'categoryId': u'25',
                u'channelId': u'channel1234',
                u'channelTitle': u'channel Title',
                u'description': u'video 1234 description',
                u'liveBroadcastContent': u'none',
                u'localized': {
                    u'description': u'description',
                    u'title': u'Video 1234'
                },
                u'publishedAt': u'2018-01-01T00:00:00.000Z',
                u'tags': [
                    u'tag1',
                    u'tag2',
                ],
                u'thumbnails': {
                    u'default': {
                        u'height': 90,
                        u'url': u'http://example.com/default.jpg',
                        u'width': 120
                    },
                    u'high': {
                        u'height': 360,
                        u'url': u'hhttp://example.com/high.jpg',
                        u'width': 480
                    },
                    u'maxres': {
                        u'height': 720,
                        u'url': u'http://example.com/maxres.jpg',
                        u'width': 1280
                    },
                    u'medium': {
                        u'height': 180,
                        u'url': u'http://example.com/medium.jpg',
                        u'width': 320
                    },
                    u'standard': {
                        u'height': 480,
                        u'url': u'http://example.com/standard.jpg',
                        u'width': 640
                    }
                },
                u'title': u'Video 1234'
            },
            u'statistics': {
                u'commentCount': u'9999',
                u'dislikeCount': u'9999',
                u'favoriteCount': u'9999',
                u'likeCount': u'9999',
                u'viewCount': u'9999'
            }
        }]
        service = mock.Mock()
        service.search().list.return_value.execute.return_value = {
            u'etag': u'"etag/123456789"',
            u'items': [{
                u'etag': u'"etag/123456789"',
                u'id': {
                    u'kind': u'youtube#video',
                    u'videoId': u'video1234'
                },
                u'kind': u'youtube#searchResult'
            }],
            u'kind': u'youtube#searchListResponse',
            u'nextPageToken': u'next_page_token',
            u'pageInfo': {
                u'resultsPerPage': 1,
                u'totalResults': 1500
            },
            u'regionCode': u'GB'
        }
        service.videos().list.return_value.execute.return_value = {
            u'etag': u'"etag/123456789"',
            u'items': expected_items,
            u'kind': u'youtube#videoListResponse',
            u'pageInfo': {
                u'resultsPerPage': 1,
                u'totalResults': 1500,
            }
        }
        client = Client(service=service)
        result = client.search('kittens')
        self.assertEqual(result, expected_items)

    def test_search_no_results(self):
        service = mock.Mock()
        service.search().list.return_value.execute.return_value = {
            u'etag': u'"etag/123456789"',
            u'items': [],
            u'kind': u'youtube#searchListResponse',
            u'nextPageToken': u'next_page_token',
            u'pageInfo': {
                u'resultsPerPage': 0,
                u'totalResults': 0
            },
            u'regionCode': u'GB'
        }
        client = Client(service=service)
        result = client.search('kittens')
        self.assertEqual(result, [])

    def test_get_video(self):
        expected_items = [{
            u'snippet': {
                u'categoryId': u'25',
                u'channelId': u'channel1234',
                u'channelTitle': u'channel Title',
                u'description': u'video 1234 description',
                u'liveBroadcastContent': u'none',
                u'localized': {
                    u'description': u'description',
                    u'title': u'Video 1234'
                },
                u'publishedAt': u'2018-01-01T00:00:00.000Z',
                u'tags': [
                    u'tag1',
                    u'tag2',
                ],
                u'thumbnails': {
                    u'default': {
                        u'height': 90,
                        u'url': u'http://example.com/default.jpg',
                        u'width': 120
                    },
                    u'high': {
                        u'height': 360,
                        u'url': u'hhttp://example.com/high.jpg',
                        u'width': 480
                    },
                    u'maxres': {
                        u'height': 720,
                        u'url': u'http://example.com/maxres.jpg',
                        u'width': 1280
                    },
                    u'medium': {
                        u'height': 180,
                        u'url': u'http://example.com/medium.jpg',
                        u'width': 320
                    },
                    u'standard': {
                        u'height': 480,
                        u'url': u'http://example.com/standard.jpg',
                        u'width': 640
                    }
                },
                u'title': u'Video 1234'
            },
            u'statistics': {
                u'commentCount': u'9999',
                u'viewCount': u'9999',
                u'favoriteCount': u'9999',
                u'dislikeCount': u'9999',
                u'likeCount': u'9999'
            },
            u'kind': u'youtube#video',
            u'etag': u'"etag/123456789"',
            u'id': u'video1234'
        }]
        service = mock.Mock()
        service.videos().list.return_value.execute.return_value = {
            u'items': expected_items,
            u'kind': u'youtube#videoListResponse',
            u'etag': u'"etag/123456789"',
            u'pageInfo': {
                u'resultsPerPage': 1,
                u'totalResults': 1
            }
        }
        client = Client(service=service)
        result = client.get('video1234')
        self.assertEqual(result, expected_items)

    def test_get_video_comments(self):
        expected_items = [{
            u'snippet': {
                u'totalReplyCount': 500,
                u'canReply': False,
                u'topLevelComment': {
                    u'snippet': {
                        u'authorChannelUrl': u'http://sample.com/channel/',
                        u'authorDisplayName': u'Some display name',
                        u'updatedAt': u'2018-01-01T00:00:00.000Z',
                        u'videoId': u'video1234',
                        u'publishedAt': u'2018-01-01T00:00:00.000Z',
                        u'viewerRating': u'none',
                        u'authorChannelId': {
                            u'value': u'channel1234'
                        },
                        u'canRate': True,
                        u'textOriginal': u"Original text",
                        u'likeCount': 7336,
                        u'authorProfileImageUrl': u'http://sample.com/pic.jpg',
                        u'textDisplay': u'Display text'
                    },
                    u'kind': u'youtube#comment',
                    u'etag': u'"etag/123456789"',
                    u'id': u'comment1234'
                },
                u'videoId': u'video1234',
                u'isPublic': True
            },
            u'kind': u'youtube#commentThread',
            u'etag': u'"foobarblah123456789"',
            u'id': u'thread1234'
        }]
        service = mock.Mock()
        service.commentThreads().list.return_value.execute.return_value = {
            u'nextPageToken': u'next_page_token',
            u'items': expected_items,
            u'kind': u'youtube#commentThreadListResponse',
            u'etag': u'"etag/123456789"',
            u'pageInfo': {
                u'resultsPerPage': 1,
                u'totalResults': 1500
            }
        }
        client = Client(service=service)
        result = client.get_video_comments('video1234')
        self.assertEqual(result, expected_items)

    def test_get_video_transcript_no_caption(self):
        # checks that None is returned if no captions are available
        service = mock.Mock()
        mock_pytube = mock.Mock()
        mock_pytube.captions.get_by_language_code.return_value = None
        client = Client(service=service)
        with mock.patch('services.youtube.YouTube', return_value=mock_pytube):
            result = client.get_video_transcript('video1234')
        self.assertEqual(result, None)

    def test_get_video_transcript(self):
        service = mock.Mock()
        mock_pytube = mock.Mock()
        mock_xml = mock.Mock()
        mock_xml.xml_captions = MOCK_CAPTIONS_XML
        mock_pytube.captions.get_by_language_code.return_value = mock_xml
        client = Client(service=service)
        with mock.patch('services.youtube.YouTube', return_value=mock_pytube):
            result = client.get_video_transcript('video1234')
        self.assertEqual(
            result, 'Hello world! Im Rob Charlwood and Im an Engineer')

    def test_get_video_transcript_utf8_chars(self):
        service = mock.Mock()
        mock_pytube = mock.Mock()
        mock_xml = mock.Mock()
        mock_xml.xml_captions = MOCK_CAPTIONS_XML_UTF8
        mock_pytube.captions.get_by_language_code.return_value = mock_xml
        client = Client(service=service)
        with mock.patch('services.youtube.YouTube', return_value=mock_pytube):
            result = client.get_video_transcript('video1234')
        self.assertEqual(
            result, u"象は鼻が長 I’m Rob Charlwood - Engineer")
