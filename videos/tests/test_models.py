# -*- coding: utf-8 -*-
from djangae.test import TestCase

from core.tests.factories import VideoFactory


class VideoModelTestCase(TestCase):
    def test_unicode_method(self):
        video = VideoFactory.create(name=u'象は鼻が長')
        self.assertEqual(video.__unicode__(), u'象は鼻が長')
