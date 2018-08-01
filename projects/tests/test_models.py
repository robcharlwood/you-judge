# -*- coding: utf-8 -*-
from djangae.test import TestCase

from core.tests.factories import ProjectFactory


class ProjectModelTestCase(TestCase):
    def test_unicode_method(self):
        project = ProjectFactory.create(name=u'象は鼻が長')
        self.assertEqual(project.__unicode__(), u'象は鼻が長')
