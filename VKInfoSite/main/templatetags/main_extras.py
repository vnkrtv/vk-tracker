# pylint: disable=invalid-name
"""Custom template tags"""
from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def neo4j_url():
    """Neo4j DB Browser url"""
    return settings.DATABASES['neo4j']['URL']


@register.simple_tag
def sex(value):
    """Converts sex code to string"""
    if value == 1:
        return 'Female'
    return 'Male'


@register.simple_tag
def languages(value):
    """Converts list with languages to string"""
    return ', '.join(value)


@register.simple_tag
def schools(schools_list):
    """Converts dict with schools to string"""
    schools_str = ''
    for school in schools_list:
        if school.get('year_from') and school.get('year_to'):
            schools_str += '%s %s-%s, ' % (school['name'], school['year_from'], school['year_to'])
        else:
            schools_str += '%s, ' % school['name']
    schools_str = schools_str[:-2]
    return schools_str


@register.simple_tag
def main_info_name(name):
    """Capitalize features names for displaying"""
    if name == 'photo_id':
        name = 'Avatar Photo ID'
        return name
    name = ' '.join([s.capitalize() for s in name.split('_')])
    return name


@register.simple_tag
def sort_icon():
    """Sort icon source"""
    return '/static/main/images/sort.svg'


@register.simple_tag
def eye_icon():
    """Eye icon source"""
    return '/static/main/images/eye-solid.svg'
