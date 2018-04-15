from django.conf.urls import include, url
from django.contrib import admin
from django.shortcuts import get_object_or_404, get_list_or_404
from django.db.models import Count
from django.conf import settings
from marksapp.models import Bookmark, Tag

urlpatterns = [
    url(r'^', include('marksapp.urls')),
    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
