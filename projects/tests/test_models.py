from djangae.test import TestCase

from core.tests.factories import ProjectFactory


class ProjectModelTestCase(TestCase):
    def test_unicode_method(self):
        project = ProjectFactory.create(name='Foo')
        self.assertEqual(project.__unicode__(), 'Foo')
