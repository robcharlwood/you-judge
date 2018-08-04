from djangae.test import TestCase

import mock

from core.tests.factories import VideoFactory
from videos.models import VideoComment
from videos.tasks import (
    cloudnlp_analyze_transcript,
    youtube_import_comments,
    youtube_import_transcript
)


class YoutubeImportCommentsTestCase(TestCase):
    def test_video_does_not_exist(self):
        resp = youtube_import_comments(9999)
        self.assertEqual(None, resp)
        self.assertEqual(0, len(VideoComment.objects.all()))

    def test_youtube_client_exception(self):
        video = VideoFactory()
        service = mock.Mock()
        service.get_video_comments.side_effect = Exception
        with mock.patch('videos.tasks.youtube.Client') as mock_yt:
            mock_yt.return_value = service
            resp = youtube_import_comments(video.pk)
            self.assertEqual(None, resp)
        self.assertEqual(0, len(VideoComment.objects.all()))

    def test_no_comments_returned(self):
        video = VideoFactory()
        service = mock.Mock()
        service.get_video_comments.return_value = []
        with mock.patch('videos.tasks.youtube.Client') as mock_yt:
            mock_yt.return_value = service
            resp = youtube_import_comments(video.pk)
            self.assertEqual(None, resp)
        self.assertEqual(0, len(VideoComment.objects.all()))

    def test_ok(self):
        expected_comments = [{
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
        video = VideoFactory()
        service = mock.Mock()
        service.get_video_comments.return_value = expected_comments
        with mock.patch('videos.tasks.youtube.Client') as mock_yt:
            mock_yt.return_value = service
            resp = youtube_import_comments(video.pk)
            self.assertEqual(None, resp)
        self.assertEqual(1, len(VideoComment.objects.all()))


class YoutubeImportTranscriptTestCase(TestCase):
    def test_video_does_not_exist(self):
        resp = youtube_import_transcript(9999)
        self.assertEqual(None, resp)

    def test_youtube_client_exception(self):
        video = VideoFactory(transcript='')
        service = mock.Mock()
        service.get_video_transcript.side_effect = Exception
        with mock.patch('videos.tasks.youtube.Client') as mock_yt:
            mock_yt.return_value = service
            resp = youtube_import_transcript(video.pk)
            self.assertEqual(None, resp)
        video.refresh_from_db()
        self.assertEqual('', video.transcript)

    def test_no_transcript_returned(self):
        video = VideoFactory(transcript='')
        service = mock.Mock()
        service.get_video_transcript.return_value = None
        with mock.patch('videos.tasks.youtube.Client') as mock_yt:
            mock_yt.return_value = service
            resp = youtube_import_transcript(video.pk)
            self.assertEqual(None, resp)
        video.refresh_from_db()
        self.assertEqual('', video.transcript)

    def test_ok(self):
        video = VideoFactory(transcript='')
        service = mock.Mock()
        service.get_video_transcript.return_value = 'Im a transcript.'
        with mock.patch('videos.tasks.youtube.Client') as mock_yt:
            mock_yt.return_value = service
            resp = youtube_import_transcript(video.pk)
            self.assertEqual(None, resp)
        video.refresh_from_db()
        self.assertEqual(video.transcript, 'Im a transcript.')


class CloudnlpAnalyzeTranscriptTestCase(TestCase):
    def test_video_does_not_exist(self):
        resp = cloudnlp_analyze_transcript(9999)
        self.assertEqual(None, resp)

    def test_video_does_not_have_transcript(self):
        video = VideoFactory(transcript='')
        resp = cloudnlp_analyze_transcript(video.pk)
        self.assertEqual(None, resp)
        video.refresh_from_db()
        self.assertEqual({}, video.analyzed_transcript)
        self.assertEqual(0, video.sentiment)
        self.assertEqual(0, video.magnitude)

    def test_cloudnlp_client_exception(self):
        video = VideoFactory(transcript='Hello world!')
        service = mock.Mock()
        service.analyze_sentiment.side_effect = Exception
        with mock.patch('videos.tasks.cloudnlp.Client') as mock_cloudnlp:
            mock_cloudnlp.return_value = service
            resp = cloudnlp_analyze_transcript(video.pk)
            self.assertEqual(None, resp)
        video.refresh_from_db()
        self.assertEqual({}, video.analyzed_transcript)
        self.assertEqual(0, video.sentiment)
        self.assertEqual(0, video.magnitude)

    def test_ok(self):
        mock_analysis = {
            'documentSentiment': {
                'score': -0.8,
                'magnitude': 17.0
            }
        }
        video = VideoFactory(transcript='Hello world!')
        service = mock.Mock()
        service.analyze_sentiment.return_value = mock_analysis
        with mock.patch('videos.tasks.cloudnlp.Client') as mock_cloudnlp:
            mock_cloudnlp.return_value = service
            resp = cloudnlp_analyze_transcript(video.pk)
            self.assertEqual(None, resp)
        video.refresh_from_db()
        self.assertEqual(mock_analysis, video.analyzed_transcript)
        self.assertEqual(-0.8, video.sentiment)
        self.assertEqual(17.0, video.magnitude)
