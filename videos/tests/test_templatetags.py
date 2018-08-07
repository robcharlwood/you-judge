from djangae.test import TestCase

from videos.templatetags.sentiment import sentiment_display
from videos.templatetags.charts import pie_chart


class SentimentDisplayTagTestCase(TestCase):
    def test_sentiment_score_is_none(self):
        self.assertEqual(None, sentiment_display(None))

    def test_sentiment_score_is_neutral(self):
        self.assertEqual('Neutral', sentiment_display(0.0))

    def test_sentiment_score_is_positive(self):
        self.assertEqual('Positive', sentiment_display(0.8))

    def test_sentiment_score_is_negative(self):
        self.assertEqual('Negative', sentiment_display(-0.8))


class PieChartTagTestCase(TestCase):
    def test_chart_ok(self):
        resp = pie_chart(
            'Foo Bar', ['Foo', 'Bar'], {'foo': 1,  'bar': 2},
            width='900px', height='400px')
        expected_context = {
            'id': 'foo-bar',
            'title': 'Foo Bar',
            'headers': ['Foo', 'Bar'],
            'values': {'foo': 1,  'bar': 2},
            'width': '900px',
            'height': '400px',
        }
        self.assertEqual(expected_context, resp)
