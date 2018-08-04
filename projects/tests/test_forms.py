from djangae.test import TestCase

from core.tests.factories import UserFactory
from projects.forms import ProjectForm


class ProjectFormTestCase(TestCase):
    def test_form_valid(self):
        user = UserFactory()
        form = ProjectForm(data={'name': 'Hello World!'})
        self.assertTrue(form.is_valid())
        project = form.save(commit=False)
        project.owner = user
        project.save()
        self.assertEqual(project.name, 'Hello World!')
        self.assertEqual(project.owner, user)
        self.assertIsNotNone(project.created)
        self.assertIsNotNone(project.modified)
