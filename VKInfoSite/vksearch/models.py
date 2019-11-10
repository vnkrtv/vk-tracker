from django.db import models
from django import template


# Create your models here.
register = template.Library()
@register.filter(name='lookup')
def lookup(d, key):
    return d[key]
