# -*- coding: utf-8 -*-
from djangae.test import TestCase

from core.tests.factories import VideoCommentFactory, VideoFactory


class VideoModelTestCase(TestCase):
    def test_unicode_method(self):
        video = VideoFactory.create(name=u'象は鼻が長')
        self.assertEqual(video.__unicode__(), u'象は鼻が長')


class VideoCommentTestCase(TestCase):
    def test_unicode_method(self):
        video = VideoFactory()
        comment = VideoCommentFactory.create(video=video, comment=u'象は鼻が長')
        self.assertEqual(
            comment.__unicode__(), u'Video: {} Comment: 象は鼻が長'.format(
                video.pk))
