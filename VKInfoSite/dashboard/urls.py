# pylint: skip-file
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('<domain>', views.dashboard, name='dash')
]
