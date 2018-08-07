# -*- coding: utf-8 -*-
from djangae.test import TestCase

from core.tests.factories import VideoCommentFactory, VideoFactory


class VideoModelTestCase(TestCase):
    def test_unicode_method(self):
        video = VideoFactory.create(name=u'象は鼻が長')
        self.assertEqual(video.__unicode__(), u'象は鼻が長')

    def test_can_be_analyze_property(self):
        video = VideoFactory(transcript='')
        self.assertFalse(video.can_be_analyzed)
        video.transcript = 'foo'
        video.save()
        self.assertTrue(video.can_be_analyzed)

    def test_analysis_complete_property(self):
        video = VideoFactory(sentiment=0, magnitude=0, analyzed_transcript={})
        self.assertFalse(video.analysis_complete)
        video.sentiment = 0.8
        video.magnitude = 0.8
        video.analyzed_transcript = {'foo': 'bar'}
        video.save()
        self.assertTrue(video.analysis_complete)

    def test_comment_analysis_complete_property(self):
        video = VideoFactory(sentiment=0, magnitude=0, analyzed_transcript={})
        VideoCommentFactory(
            video=video, analyzed_comment={'foo': 'foo'})
        comment_2 = VideoCommentFactory(video=video, analyzed_comment={})
        self.assertFalse(video.comment_analysis_complete)
        comment_2.analyzed_comment = {'bar': 'bar'}
        comment_2.save()
        self.assertTrue(video.comment_analysis_complete)


class VideoCommentTestCase(TestCase):
    def test_unicode_method(self):
        video = VideoFactory()
        comment = VideoCommentFactory.create(
            video=video, comment_raw=u'象は鼻が長')
        self.assertEqual(
            comment.__unicode__(), u'Video: {} Comment: 象は鼻が長'.format(
                video.pk))

    def test_analysis_complete_property(self):
        comment = VideoCommentFactory(
            sentiment=0, magnitude=0, analyzed_comment={})
        self.assertFalse(comment.analysis_complete)
        comment.sentiment = 0.8
        comment.magnitude = 0.8
        comment.analyzed_comment = {'foo': 'bar'}
        comment.save()
        self.assertTrue(comment.analysis_complete)
