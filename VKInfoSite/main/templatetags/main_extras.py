from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def neo4j_url():
    return settings.DATABASES['neo4j']['URL']


@register.simple_tag
def sex(value):
    if value == 1:
        return 'Female'
    return 'Male'


@register.simple_tag
def languages(value):
    return ', '.join(value)


@register.simple_tag
def schools(schools_list):
    s = ''
    for school in schools_list:
        if school.get('year_from') and school.get('year_to'):
            s += '%s %s-%s, ' % (school['name'], school['year_from'], school['year_to'])
        else:
            s += '%s, ' % school['name']
    s = s[:-2]
    return s


@register.simple_tag
def sort_icon():
    return '/static/main/images/sort.svg'


@register.simple_tag
def eye_icon():
    return '/static/main/images/eye-solid.svg'
