# accounts/templatetags/user_extras.py

from django import template

register = template.Library()

@register.filter
def initials(user):
    first = user.first_name[0] if user.first_name else ''
    last = user.last_name[0] if user.last_name else ''
    return (first + last).upper()
