from django.conf.urls import include, url
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add/$', views.add_mark, name='add_mark'),
    #url(r'^orphans/$', views.orphans, name='orphans'),
    url(r'^mark/(?P<id>[0-9]+)/$', views.edit_mark, name='edit_mark'),
    url(r'^mark/(?P<id>[0-9]+)/delete/$', views.delete_mark, name='delete_mark'),
    url(r'^tag/(?P<slug>[-\w\d+]+)/$', views.tag, name='tag'),
    url(r'^tag/(?P<slug>[-\w\d+]+)/delete/$', views.delete_tag, name='delete_tag'),
    url(r'^tag/(?P<slug1>[-\w\d+]+)/merge/(?P<slug2>[-\w\d+]+)$', views.merge, name='merge'),
    url(r'^api/mark/(?P<id>[0-9]+)/$', views.api_mark, name='api_mark'),
    url(r'^api/tags/(?P<prefix>[-\w\d+]+)$', views.api_tags, name='api_tags'),
    url(r'^api/tags/', views.api_tags, name='api_tags'),
    url(r'^api/get_title/$', views.api_get_title, name='api_get_title'),
    url(r'^api/delete_mark/(?P<id>[0-9]+)/$', views.api_delete_mark, name='api_delete_mark'),
    url(r'^block/mark/(?P<id>[0-9]+)/$', views.edit_mark_form, name='edit_mark_form'),
    url(r'^edit_selection/$', views.edit_selection, name='edit_selection'),
    url(r'^(?P<username>\w+)/search/$', views.search, name='search'),
    url(r'^(?P<username>\w+)/tag/(?P<slug>[-\w\d+]+)/$', views.user_tag, name='user_tag'),
    url(r'^(?P<username>\w+)/tag/$', views.user_tag, name='user_tag'),
    url(r'^(?P<username>\w+)$', views.user_index, name='user_index'),
    url(r'^import_netscape/$', views.import_netscape, name='import_netscape'),
    url(r'^import_json/$', views.import_json, name='import_json'),
    url(r'^export_json/$', views.export_json, name='export_json'),
    url(r'^changelog/$', views.changelog, name='changelog'),
    url(r'^', include('registration.backends.hmac.urls')),
    #url(r'^', include('django.contrib.auth.urls')),
]
