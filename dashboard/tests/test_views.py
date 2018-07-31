from djangae.test import TestCase
from django.test import RequestFactory

from dashboard.views import DashboardView


class DashboardViewTestCase(TestCase):
    def test_200_ok(self):
        factory = RequestFactory()
        request = factory.get('/')
        resp = DashboardView.as_view()(request)
        self.assertEqual(resp.status_code, 200)
