from django import template

register = template.Library()


@register.simple_tag
def sentiment_display(sentiment_score):
    """
    Returns a human readable display value for a sentiment score
    """
    if sentiment_score is None:
        return None
    sentiment = 'Neutral'
    if sentiment_score < 0:
        sentiment = 'Negative'
    elif sentiment_score > 0:
        sentiment = 'Positive'
    return sentiment
