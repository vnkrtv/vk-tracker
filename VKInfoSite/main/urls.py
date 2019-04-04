from django.conf.urls import url, include
from . import views

app_name = 'main'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^user_info/$', views.getUserDomainShowData, name='getUserDomainShowData'),
    url(r'^user_changes/$', views.getUserDomainChanges, name='getUserDomainChanges'),
    url(r'^users_relation/$', views.getUserDomains, name='getUserDomains'),
    url(r'^user_info/show_data/$', views.getUserInfo, name='getUserInfo'),
    url(r'^user_changes/show_changes/$', views.getUserChanges, name='getUserChanges'),
    url(r'^user_changes/get_date/$', views.getUserOldInfo, name='getUserOldInfo'),
    url(r'^users_relation/show_relation/$', views.getUsersRelations, name='getUsersRelations')
]