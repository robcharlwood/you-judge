from djangae.test import TestCase

from videos.templatetags.sentiment import sentiment_display


class SentimentDisplayTagTestCase(TestCase):
    def test_sentiment_score_is_none(self):
        self.assertEqual(None, sentiment_display(None))

    def test_sentiment_score_is_neutral(self):
        self.assertEqual('Neutral', sentiment_display(0.0))

    def test_sentiment_score_is_positive(self):
        self.assertEqual('Positive', sentiment_display(0.8))

    def test_sentiment_score_is_negative(self):
        self.assertEqual('Negative', sentiment_display(-0.8))
