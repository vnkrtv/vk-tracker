from django.conf.urls import url, include
from . import views

app_name = 'main'

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^add_user/$', views.getDomainAdd, name='getDomainAdd'),
    url(r'^add_user/show_result/$', views.addResult, name='addUserResult'),

    url(r'^user_info/$', views.getDomainInfo, name='getDomainInfo'),
    url(r'^user_info/show_info/$', views.getInfo, name='getInfo'),

    url(r'^user_changes/$', views.getDomainChanges, name='getDomainChanges'),
    url(r'^user_changes/show_changes/$', views.getChanges, name='getChanges'),
    url(r'^user_changes/get_date/$', views.getOldInfo, name='getOldInfo'),

    url(r'^users_relation/$', views.getDomains, name='getDomains'),
    url(r'^users_relation/show_relation/$', views.getRelations, name='getRelations')
]