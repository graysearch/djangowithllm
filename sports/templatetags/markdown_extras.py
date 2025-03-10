import markdown
from django import template

register = template.Library()

@register.filter
def markdownify(text):
    """
    Converts markdown text to HTML.
    """
    return markdown.markdown(text)
