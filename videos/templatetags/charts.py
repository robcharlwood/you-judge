from django import template
from django.utils.text import slugify

register = template.Library()


@register.inclusion_tag('includes/pie_chart.html')
def pie_chart(title, headers, values, width='100%', height='250px'):
    """
    Returns a pie chart for the passed data
    """
    return {
        'id': slugify(title),
        'title': title,
        'headers': headers,
        'values': values,
        'width': width,
        'height': height,
    }
