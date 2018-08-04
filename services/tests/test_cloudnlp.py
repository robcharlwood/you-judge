from djangae.test import TestCase

import mock

from services.cloudnlp import Client


class CloudNaturalLanguageClientTestCase(TestCase):
    def test_analyze_sentiment(self):
        mock_analysis = {
            "documentSentiment": {
                "score": 0.2,
                "magnitude": 3.6
            },
            "language": "en",
            "sentences": [{
                # positive
                "text": {
                    "content": "Rob is awesome",
                    "beginOffset": 0
                },
                "sentiment": {
                    "magnitude": 0.8,
                    "score": 0.8
                }
            }, {
                # negative
                "text": {
                    "content": "Rob is rubbish",
                    "beginOffset": 0
                },
                "sentiment": {
                    "magnitude": 0.8,
                    "score": -0.8
                }
            }, {
                # neutral
                "text": {
                    "content": "My name is Rob",
                    "beginOffset": 0
                },
                "sentiment": {
                    "magnitude": 0.0,
                    "score": 0.0
                }
            }]
        }
        service = mock.Mock()
        service.documents().analyzeSentiment.\
            return_value.execute.return_value = mock_analysis
        client = Client(service=service)
        text = 'Rob is awesome\nRob is rubbish\nMy name is Rob'
        result = client.analyze_sentiment(text)
        self.assertEqual(result, mock_analysis)
