from django.conf.urls import url, include
from . import views

app_name = 'vksearch'

urlpatterns = [
    url(r'^search/$',         views.get_search_params,      name='get_search_params'),
    url(r'^result/$',         views.get_result,             name='get_result'),

    url(r'^add_philter_1/$', views.get_new_philter_countries,          name='get_new_philter_countries'),
    url(r'^add_philter_2/$', views.get_new_philter_region,             name='get_new_philter_region'),
    url(r'^add_philter_3/$', views.get_new_philter_cities,             name='get_new_philter_cities'),
    url(r'^add_philter_4/$', views.get_new_philter_universities,       name='get_new_philter_universities'),
    url(r'^add_philter_5/$', views.get_new_philter_friends_and_groups, name='get_new_philter_friends_and_groups'),
    url(r'^add_philter_6/$', views.add_new_philter,                    name='add_new_philter')
]