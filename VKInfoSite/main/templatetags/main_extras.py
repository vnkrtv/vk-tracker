from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def neo4j_url():
    return settings.DATABASES['neo4j']['URL']


@register.simple_tag
def sort_icon():
    return '/static/main/images/sort.svg'


@register.simple_tag
def eye_icon():
    return '/static/main/images/eye-solid.svg'
