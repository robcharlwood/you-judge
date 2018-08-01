from djangae.test import TestCase

from projects.forms import ProjectForm


class ProjectFormTestCase(TestCase):
    def test_form_valid(self):
        form = ProjectForm(data={'name': 'Hello World!'})
        self.assertTrue(form.is_valid())
        project = form.save()
        self.assertEqual(project.name, 'Hello World!')
        self.assertIsNotNone(project.created)
        self.assertIsNotNone(project.modified)
