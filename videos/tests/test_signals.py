from djangae.test import TestCase

import mock

from core.tests.factories import VideoFactory
from videos import tasks


class VideoPostSaveTestCase(TestCase):
    def test_post_save_created(self):
        with mock.patch('google.appengine.ext.deferred.defer') as mock_defer:
            video = VideoFactory()
            self.assertTrue(mock_defer.called)
            self.assertEqual(2, mock_defer.call_count)
            self.assertEqual(
                mock_defer.call_args_list, [
                    mock.call(
                        tasks.youtube_import_comments,
                        video.pk,
                        _queue='comments'),
                    mock.call(
                        tasks.youtube_import_transcript,
                        video.pk,
                        _queue='videos')],
                )

    def test_post_save_existing(self):
        video = VideoFactory()
        with mock.patch('google.appengine.ext.deferred.defer') as mock_defer:
            video.save()
            self.assertFalse(mock_defer.called)
            self.assertEqual(0, mock_defer.call_count)
