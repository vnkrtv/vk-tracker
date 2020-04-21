from django.conf.urls import url
from . import views

app_name = 'main'

urlpatterns = [
    url(r'^$',views.login_page, name='login_page'),

    url(r'^settings/$', views.change_settings, name='change_settings'),
    url(r'^change_settings_result/&', views.change_settings_result, name='change_settings_result'),

    url(r'^add_user/$', views.add_user, name='add_user'),
    url(r'^add_user/show_result/$', views.add_user_result, name='add_user_result'),

    url(r'^user_info/$', views.user_info, name='user_info'),
    url(r'^user_info/show_info/$', views.get_user_info, name='get_user_info'),

    url(r'^user_changes/$', views.get_changes, name='get_changes'),
    url(r'^user_changes/get_date/$', views.get_dates, name='get_dates'),
    url(r'^user_changes/show_changes/$', views.get_user_changes,name='get_user_changes'),

    url(r'^users_relation/$',               views.get_mutual_activity,            name='get_mutual_activity'),
    url(r'^users_relation/get_dates/$',     views.get_users_dates,        name='get_users_dates'),
    url(r'^users_relation/show_relation/$', views.get_relations,          name='get_relations'),
]

#leaflet/folium instagram_scrapper