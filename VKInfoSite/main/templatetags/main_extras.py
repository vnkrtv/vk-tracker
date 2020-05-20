from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def neo4j_url():
    return settings.DATABASES['neo4j']['URL']
