from django.urls import include, path, re_path
from marksapp.misc import multitag_regex

from . import views

urlpatterns = [
    re_path(r"^$", views.index, name="index"),
    re_path(r"^add/$", views.add_mark, name="add_mark"),
    re_path(r"^mark/(?P<id>[0-9]+)/delete/$", views.delete_mark, name="delete_mark"),
    # api
    re_path(r"^api/mark/(?P<id>[0-9]+)/$", views.api_mark, name="api_mark"),
    re_path(r"^api/tags/(?P<prefix>[-\w\d+]+)$", views.api_tags, name="api_tags"),
    re_path(r"^api/tags/", views.api_tags, name="api_tags"),
    re_path(r"^api/get_title/$", views.api_get_title, name="api_get_title"),
    re_path(
        r"^api/delete_mark/(?P<id>[0-9]+)/$",
        views.api_delete_mark,
        name="api_delete_mark",
    ),
    re_path(r"^api/delete_marks/$", views.api_delete_marks, name="api_delete_marks"),
    re_path(r"^api/edit_multiple/$", views.api_edit_multiple, name="api_edit_multiple"),
    re_path(
        r"^api/bump_mark/(?P<id>[0-9]+)/$", views.api_bump_mark, name="api_bump_mark"
    ),
    re_path(
        r"^block/mark/(?P<id>[0-9]+)/$", views.edit_mark_form, name="edit_mark_form"
    ),
    # user views
    re_path(
        r"^(?P<username>\w+)/mark/(?P<id>[0-9]+)/$",
        views.mark_permalink,
        name="mark_permalink",
    ),
    re_path(
        r"^(?P<username>\w+)/tag/(?P<slug>{})/$".format(multitag_regex[1:-1]),
        views.user_tag,
        name="user_tag",
    ),
    re_path(r"^(?P<username>\w+)/tag/$", views.user_tag, name="user_tag"),
    re_path(r"^(?P<username>\w+)$", views.user_index, name="user_index"),
    re_path(r"^profile/$", views.user_profile, name="user_profile"),
    re_path(r"^import_netscape/$", views.import_netscape, name="import_netscape"),
    re_path(r"^import_json/$", views.import_json, name="import_json"),
    re_path(r"^export_json/$", views.export_json, name="export_json"),
    re_path(r"^changelog/$", views.changelog, name="changelog"),
    re_path(r"^register/$", views.register, name="register"),
    re_path(r"^guide/$", views.guide, name="guide"),
    re_path(
        r"^",
        include("django.contrib.auth.urls"),
        {"extra_context": {"page_title": "login"}},
    ),
]
