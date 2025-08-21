
from django import template

register = template.Library()

@register.filter
def get_percent(used, total):
    try:
        return int((used / total) * 100)
    except ZeroDivisionError:
        return 0
