from django.urls import re_path
from django.conf.urls import url, include
from .views import dash, dash_ajax

app_name = 'dashboard'

urlpatterns = [
    re_path(r'_', dash_ajax),
    re_path(r'', dash)
]
