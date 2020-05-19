from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def neo4j_url():
    return "http://{}:{}@{}:{}/".format(
        settings.DATABASES['neo4j']['USER'], settings.DATABASES['neo4j']['PASSWORD'],
        settings.DATABASES['neo4j']['HOST'], settings.DATABASES['neo4j']['PORT'],
        #settings.DATABASES['neo4j']["NAME"]
    )
