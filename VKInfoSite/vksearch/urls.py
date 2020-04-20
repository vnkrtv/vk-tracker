from django.conf.urls import url, include
from . import views

app_name = 'vksearch'

urlpatterns = [
    url(r'^search/$',         views.get_search_params,      name='get_search_params'),
    url(r'^result/$',         views.get_search_result,      name='get_search_result'),

    url(r'^add_filter_1/$', views.add_search_filter,          name='add_search_filter'),
    url(r'^add_filter_2/$', views.get_new_filter_cities,             name='get_new_filter_cities'),
    url(r'^add_filter_3/$', views.get_new_filter_universities,       name='get_new_filter_universities'),
    url(r'^add_filter_4/$', views.get_new_filter_friends_and_groups, name='get_new_filter_friends_and_groups'),
    url(r'^add_filter_5/$', views.get_new_filter_name,               name='get_new_filter_name'),
    url(r'^add_filter/$',   views.add_new_filter,                    name='add_new_filter'),

    url(r'^delete_filter/$',        views.delete_filter,        name='delete_filter'),
    url(r'^delete_filter_result/$', views.delete_filter_result, name='delete_filter_result'),
]