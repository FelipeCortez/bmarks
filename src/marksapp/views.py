from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, When, Case, Sum, F
from django.db.models.functions import Lower
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse
from django.core import serializers
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from marksapp.models import Bookmark, Tag
from collections import OrderedDict
import json
import pprint
import urllib.request
import marksapp.forms as forms
import marksapp.netscape as netscape
import re
import markdown

def tags_strip_split(tags):
    return tags.replace(" ", "").split(",") if tags else []

def tag_untagged(user):
    for mark in Bookmark.objects.filter(user=user, tags__isnull=True):
        mark.tags.add(Tag.objects.get_or_create(name="untagged")[0])

def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('user_index', args=[request.user.username]))
    else:
        return HttpResponseRedirect(reverse('auth_login'))

def user_index(request, username):
    get_object_or_404(User, username=username)

    search_form = forms.SearchForm()
    sort = request.GET.get('sort', '') or "name"

    bookmarks = Bookmark.objects.filter(user__username=username)
    noprivates = bookmarks.exclude(tags__name="private")

    if not request.user.is_authenticated():
        top_tags = Tag.objects.filter(bookmark__in=noprivates)
    else:
        top_tags = Tag.objects.filter(bookmark__in=bookmarks)

    top_tags = top_tags.annotate(num_marks=Count('bookmark'))

    if not request.user.is_authenticated():
        top_tags = top_tags.exclude(name="private")

    if sort == "quantity":
        top_tags = top_tags.order_by('-num_marks', 'name')
    else:
        top_tags = top_tags.order_by('name')

    context = {
        'all': bookmarks.count(),
        'sort': sort,
        'search_form': search_form,
        'tags': top_tags,
        'username': username,
        'page_title': 'home'
    }
    return render(request, "index.html", context)

def user_tag(request, username, slug=None):
    tags = slug.split("+") if slug else []

    return marks(request, username, tags)

def marks(request, username, tags=[]):
    get_object_or_404(User, username=username)

    bookmarks = Bookmark.objects.filter(user__username=username)
    sort = request.GET.get('sort', '') or "name"
    limit = request.GET.get('limit', '')

    search_query = request.GET.get('query', '')
    search_tags = request.GET.get('tags', '')
    if limit: limit = int(limit)

    if search_query:
        bookmarks = bookmarks.filter(name__search=search_query)

    if search_tags:
        for tag in tags_strip_split(search_tags):
            bookmarks = bookmarks.filter(tags__name=tag)

    for tag in tags:
        bookmarks = bookmarks.filter(tags__name=tag)

    if not request.user.is_authenticated() or username != request.user:
        bookmarks = bookmarks.exclude(tags__name="private")

    if sort == "date":
        bookmarks = bookmarks.order_by('-date_added')
    else:
        bookmarks = bookmarks.order_by(Lower("name"))

    if limit: bookmarks = bookmarks[:limit]

    tag_count = Tag.objects.filter(bookmark__in=bookmarks) \
                           .annotate(num_marks=Count('bookmark')) \
                           .order_by('-num_marks', 'name')

    context = {
        'username': username,
        'sort': sort,
        'tag_count': tag_count,
        'tags': tags,
        'query': search_query,
        'marks': bookmarks,
        'limit': limit
    }

    return render(request, "marks.html", context)

@login_required
def add_mark(request):
    if request.method == 'POST':
        form = forms.BookmarkForm(request.POST)
        # we don't want to expose user to the form but need to validate unique_together!
        if form.is_valid():
            if Bookmark.objects.filter(url=form.cleaned_data['url'], user=request.user).exists():
                return HttpResponse(form.cleaned_data['url'])
                #raise ValidationError('urlerror')
            else:
                mark = form.save(commit=False)
                mark.user = request.user
                mark.save()
                return HttpResponseRedirect(reverse('index'))
    else:
        form = forms.BookmarkForm()

    return render(request, 'add.html', {'form': form, 'page_title': 'add'})

@login_required
def edit_mark(request, id):
    mark = Bookmark.objects.get(id=id)

    if request.method == 'POST':
        form = forms.BookmarkForm(request.POST, instance=mark)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        form = forms.BookmarkForm(instance=mark)

    return render(request, 'edit_mark.html', {'form': form})

@login_required
def delete_mark(request, id):
    get_object_or_404(Bookmark, id=id).delete()

    return HttpResponseRedirect(reverse('index'))

@login_required
def merge(request, slug1, slug2):
#    bookmarks1 = Bookmark.objects.filter(tags__name=slug1)
#    bookmarks2 = Bookmark.objects.filter(tags__name=slug2)
#    tag1 = get_object_or_404(Tag, name=slug1)
#    tag2 = get_object_or_404(Tag, name=slug2)
#
#    if bookmarks1:
#        if bookmarks2:
#            tag2.delete()
#            for mark in bookmarks2:
#                mark.tags.add(tag1)
#        return HttpResponseRedirect(reverse('tag', args=[slug1]))
#
    return HttpResponseRedirect(reverse('index'))

@login_required
def delete_tag(request, slug):
    bookmarks = Bookmark.objects.filter(user=request.user, tags__name=slug)

    for mark in bookmarks:
        mark.tags.remove(Tag.objects.get(name=slug))

    tag_untagged(request.user)

    return HttpResponseRedirect(reverse('index'))

def orphans(request):
    bookmarks = Bookmark.objects.filter(tags__isnull = True).order_by(Lower("name"))

    context = {
        'marks': bookmarks,
    }

    return render(request, "search.html", context)

@login_required
def import_netscape(request):
    if request.method == 'POST':
        form = forms.NetscapeForm(request.POST, request.FILES)
        if form.is_valid():
            netscape.bookmarks_from_file(request.FILES['file'], request.user)
            return HttpResponseRedirect(reverse('index'))
    else:
        form = forms.NetscapeForm()
    return render(request, 'import.html', {'form': form, 'page_title': 'import'})

@login_required
def export_json(request):
    if Bookmark.objects.filter(user=request.user).exists():
        bookmarks = Bookmark.objects.filter(user__username=request.user.username)
        marks_dict = {"marks": []}
        for mark in bookmarks:
            mark_dict = {}
            mark_dict["name"] = mark.name
            mark_dict["url"] = mark.url
            mark_dict["date_added"] = str(mark.date_added)
            mark_dict["tags"] = []
            for tag in mark.tags.all():
                mark_dict["tags"].append(tag.name)
            marks_dict["marks"].append(mark_dict)

    return JsonResponse(marks_dict)

@login_required
def import_json(request):
    if request.method == 'POST':
        form = forms.ImportJsonForm(request.POST, request.FILES)
        marks = request.FILES['file'].read()
        marks = json.loads(marks)

        for mark in marks["marks"]:
            b = Bookmark.objects.update_or_create(user=request.user, url=mark['url'])[0]
            b.name = mark["name"]
            b.date_added = mark["date_added"]

            for tag in mark["tags"]:
                t = Tag.objects.get_or_create(name=tag)[0]
                b.tags.add(t)

            b.save()
    else:
        form = forms.ImportJsonForm()
    return render(request, 'import.html', {'form': form})

@login_required
def edit_selection(request):
    if request.method == 'POST':
        marks_ids = request.POST.getlist('check_mark')
        tags = tags_strip_split(request.POST.get('tags'))

        for mark_id in marks_ids:
            mark = Bookmark.objects.get(id=mark_id)
            for tag in tags:
                if tag[0] == "!":
                    try:
                        mark_tag = mark.tags.get(name=tag[1:])
                    except Tag.DoesNotExist:
                        mark_tag = None

                    if mark_tag:
                        mark.tags.remove(mark_tag)
                # wow what's going on here lol
                if re.match("^[-\w]+$", tag):
                    t = Tag.objects.get_or_create(name=tag)[0]
                    mark.tags.add(t)

        tag_untagged(request.user)
        return HttpResponse('success')

    return HttpResponse('success')

@login_required
def edit_mark_form(request, id):
    mark = Bookmark.objects.get(id=id)

    if request.method == 'POST':
        form = forms.BookmarkForm(request.POST, instance=mark)
        if form.is_valid():
            form.save()
            tag_untagged(request.user)
            return HttpResponse('success')
    else:
        form = forms.BookmarkForm(instance=mark)

    return render(request, 'edit_mark_form.html', {'form': form})

def changelog(request):
    with open('etc/changelog.markdown') as f:
        return HttpResponse(markdown.markdown(f.read()))

# API

def api_mark(request, id):
    mark = Bookmark.objects.get(id=id)
    mark_dict = {}
    mark_dict["name"] = mark.name
    mark_dict["url"] = mark.url
    mark_dict["tags"] = mark.tags_str()

    return JsonResponse(mark_dict)

def api_tags(request, prefix=None):
    tags = Tag.objects.all()

    if request.user.is_authenticated():
        tags = Tag.objects.filter(bookmark__user__username=request.user)

    if prefix:
        tags = tags.filter(name__startswith=prefix)

    tags = tags.annotate(num_marks=Count('bookmark')) \
               .order_by('-num_marks', 'name')

    tags_dict = {}
    tag_list = []
    for tag in tags:
        tag_dict = {}
        tag_dict["id"] = tag.id
        tag_dict["name"] = tag.name
        tag_dict["num_marks"] = tag.num_marks
        tag_list.append(tag_dict)

    tags_dict["tags"] = tag_list
    return JsonResponse(tags_dict)

@login_required
def api_get_title(request):
    if request.method == 'POST':
        url = request.POST.get('url')

        if not (url.startswith('http://') or url.startswith('https://')):
            url = 'http://' + url

        hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
               'Accept-Encoding': 'none',
               'Accept-Language': 'en-US,en;q=0.8',
               'Connection': 'keep-alive'}

        req = urllib.request.Request(url, headers=hdr)

        try:
            with urllib.request.urlopen(req) as f:
                contents = f.read().decode('UTF-8', 'backslashreplace')
                pattern = re.compile(r"<title.*?>(.+?)</title>")
                response = {"url": re.findall(pattern, contents)[0]}
                return JsonResponse(response)
        except:
            return JsonResponse({"error": "couldn't load title"})

@login_required
def api_delete_mark(request, id):
    mark = Bookmark.objects.get(id=id).delete()

    if request.method == 'POST':
        return HttpResponse('success')

@login_required
def api_bump_mark(request, id):
    mark = get_object_or_404(Bookmark, id=id)
    mark.date_added = now()
    mark.save()

    if request.method == 'POST':
        return HttpResponse('success')
