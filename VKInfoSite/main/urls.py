from django.conf.urls import url, include
from . import views

app_name = 'main'

urlpatterns = [
    url(r'^$',                              views.index,                  name='index'),
    url(r'^settings/$',                     views.change_settings,        name='change_settings'),
    url(r'^changes_result/&',               views.change_settings_result, name='change_settings_result'),

    url(r'^add_user/$',                     views.get_domain_add,         name='get_domain_add'),
    url(r'^add_user/show_result/$',         views.add_result,             name='add_result'),

    url(r'^user_info/$',                    views.get_domain_info,        name='get_domain_info'),
    url(r'^user_info/show_info/$',          views.get_info,               name='get_info'),

    url(r'^user_changes/$',                 views.get_domain_changes,     name='get_domain_changes'),
    url(r'^user_changes/get_date/$',        views.get_dates,              name='get_dates'),
    url(r'^user_changes/show_changes/$',    views.get_changes,            name='get_changes'),

    url(r'^users_relation/$',               views.get_domains,            name='get_domains'),
    url(r'^users_relation/get_dates/$',     views.get_users_dates,        name='get_users_dates'),
    url(r'^users_relation/show_relation/$', views.get_relations,          name='get_relations')
]