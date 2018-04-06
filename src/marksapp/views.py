from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, When, Case, Sum, F
from django.db.models.functions import Lower
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.core import serializers
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from marksapp.models import Bookmark, Tag, Profile
from collections import OrderedDict
import json
import urllib.request
import marksapp.forms as forms
import marksapp.netscape as netscape
import re
import markdown

def tags_strip_split(tags):
    return tags.replace(",", " ").split() if tags else []

def tag_untagged(user):
    for mark in Bookmark.objects.filter(user=user, tags__isnull=True):
        mark.tags.add(Tag.objects.get_or_create(name="untagged")[0])

def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('user_index', args=[request.user.username]))
    else:
        return HttpResponseRedirect(reverse('login'))

def user_index(request, username):
    get_object_or_404(User, username=username)

    try:
        profile = Profile.objects.get(user__username=username)
    except ObjectDoesNotExist:
        profile = None

    sort = request.GET.get('sort', '') or "name"

    bookmarks = Bookmark.objects.filter(user__username=username)

    if not username == request.user.username:
        if profile and profile.visibility == Profile.PRIVATE:
            bookmarks = bookmarks.filter(tags__name="public")
        else:
            bookmarks = bookmarks.exclude(tags__name="private")

        bookmarks = bookmarks.exclude(tags__name__startswith=".")

    top_tags = Tag.objects.filter(bookmark__in=bookmarks) \
                          .annotate(num_marks=Count('bookmark'))

    if not request.user.is_authenticated():
        top_tags = top_tags.exclude(name="private")

    if sort == "quantity":
        top_tags = top_tags.order_by('-num_marks', 'name')
    else:
        top_tags = top_tags.order_by('name')

    context = {
        'all': bookmarks.count(),
        'sort': sort,
        'tags': top_tags,
        'username': username,
        'page_title': 'home'
    }
    return render(request, "index.html", context)

def user_profile(request):
    username = request.user.username
    user_object = User.objects.get(username__iexact=username)
    profile_object = Profile.objects.get_or_create(user=request.user)[0]

    if request.method == 'POST':
        user_form = forms.UserForm(request.POST, instance=user_object)
        profile_form = forms.ProfileForm(request.POST, instance=profile_object)
        if profile_form.is_valid() and user_form.is_valid():
            user_form.save()
            profile_form.save()
            return HttpResponseRedirect(reverse('index'))
    else:

        user_form = forms.UserForm(instance=user_object)
        profile_form = forms.ProfileForm(instance=profile_object)

    context = {
        'username': username,
        'user_form': user_form,
        'profile_form': profile_form,
        'page_title': 'profile'
    }

    return render(request, "profile.html", context)

def user_tag(request, username, slug=None):
    tags = slug.split("+") if slug else []

    return marks(request, username, tags)

def get_param(request, param, params, default=None):
    value = request.GET.get(param, '')
    if value:
        params.update({param: value})

    return value

def marks(request, username, tags=[]):
    get_object_or_404(User, username=username)

    context = {'username': username}
    params = {}

    bookmarks = Bookmark.objects.filter(user__username=username)

    limit = 100

    if get_param(request, "search_title", params):
        bookmarks = bookmarks.filter(name__search=params["search_title"])

    if get_param(request, "search_tags", params):
        for tag in tags_strip_split(params["search_tags"]):
            bookmarks = bookmarks.filter(tags__name=tag)

    if get_param(request, "search_description", params):
        bookmarks = bookmarks.filter(description__search=params["search_description"])

    for tag in tags:
        bookmarks = bookmarks.filter(tags__name=tag)

    if not username == request.user.username:
        bookmarks = bookmarks.exclude(tags__name="private")
        if not tags:
            bookmarks = bookmarks.exclude(tags__name__startswith=".")

    if get_param(request, "sort", params) and params["sort"] == "name":
        bookmarks = bookmarks.annotate(name_lower=Lower('name'))
        sorted_bookmarks = bookmarks.order_by("name_lower")
        sort = "name"
    else:
        sorted_bookmarks = bookmarks.order_by('-date_added')
        sort = "date"

    if get_param(request, "after", params):
        after_id = int(params["after"])
        after_mark = Bookmark.objects.get(id=after_id)
        if sort == "date":
            bookmarks = sorted_bookmarks.exclude(date_added__gte=after_mark.date_added)
        elif sort == "name":
            lower_name = after_mark.name.lower()
            bookmarks = sorted_bookmarks.exclude(name_lower__lte=lower_name)
        bookmarks = bookmarks[:limit]
    elif get_param(request, "before", params):
        before_id = int(params["before"])
        before_mark = Bookmark.objects.get(id=before_id)

        if sort == "date":
            bookmarks = bookmarks.order_by('date_added')
            bookmarks = bookmarks.filter(date_added__gt=before_mark.date_added)
        elif sort == "name":
            bookmarks = bookmarks.order_by(Lower("name").desc())
            lower_name = before_mark.name.lower()
            bookmarks = bookmarks.filter(name_lower__lt=lower_name)
        bookmarks = bookmarks[:limit:-1]

    else:
        bookmarks = sorted_bookmarks[:limit]

    params_str = "&".join(["{}={}".format(param, value) for param, value in params.items()])

    if bookmarks:
        if bookmarks[0] != sorted_bookmarks.first():
            before_mark = bookmarks[0]
        else:
            before_mark = None

        if bookmarks[len(bookmarks) - 1] != sorted_bookmarks[len(sorted_bookmarks) - 1]:
            after_mark = bookmarks[len(bookmarks) - 1]
        else:
            after_mark = None

        tag_count = Tag.objects.filter(bookmark__in=bookmarks) \
                            .annotate(num_marks=Count('bookmark')) \
                            .order_by('-num_marks', 'name')

        context.update({
            'marks': bookmarks,
            'sort': sort,
            'tag_count': tag_count,
            'tags': tags,
            'before_mark': before_mark,
            'after_mark': after_mark,
            'params': params,
            'params_str': params_str,
        })

    return render(request, "marks.html", context)

@login_required
def add_mark(request):
    if request.method == 'POST':
        form = forms.BookmarkForm(request.POST)
        # we don't want to expose user to the form but need to validate unique_together!
        if form.is_valid():
            if form.cleaned_data['url'] and Bookmark.objects.filter(url=form.cleaned_data['url'], user=request.user).exists():
                existing_mark = Bookmark.objects.get(url=form.cleaned_data['url'], user=request.user)
                # TODO: maybe a warning would be good
                return HttpResponseRedirect(reverse('mark_permalink', kwargs={"username": request.user.username, "id": existing_mark.id}))
            else:
                mark = form.save(commit=False)
                mark.user = request.user
                mark.save()
                return HttpResponseRedirect(reverse('index'))
    else:
        form = forms.BookmarkForm()

    return render(request, 'add.html', {'form': form, 'page_title': 'add'})

def mark_permalink(request, username, id):
    user_object = User.objects.get(username__iexact=username)
    mark = Bookmark.objects.get(id=id)

    try:
        profile = Profile.objects.get(user=user_object)
    except ObjectDoesNotExist:
        profile = None

    if username == request.user.username:
        private = False
    else:
        if profile and profile.visibility == Profile.PRIVATE:
            private = not bool(mark.tags.filter(name__iexact="public").first())
        else:
            private = bool(mark.tags.filter(name__iexact="private").first())

    if user_object == mark.user and not private:
        context = {
            'mark': mark
        }

        return render(request, 'mark_permalink.html', context)
    else:
        return HttpResponseRedirect(reverse('user_index', kwargs={"username": username}))

@login_required
def delete_mark(request, id):
    get_object_or_404(Bookmark, id=id).delete()

    return HttpResponseRedirect(reverse('index'))

@login_required
def api_delete_marks(request):
    if request.method == 'POST':
        for mark_id in request.POST.getlist("check_mark"):
            mark = Bookmark.objects.get(id=mark_id)
            if mark.user == request.user:
                mark.delete()
        return HttpResponse('success')
    return HttpResponse('failure')

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
                # optional dot, word characters, hyphens allowed
                if re.match("^\.?[-\w]+$", tag):
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

def register(request):
    context = {}
    context["page_title"] = "register"

    if request.method == 'POST':
        form = forms.RegistrationForm(request.POST)
        # we don't want to expose user to the form but need to validate unique_together!
        if form.is_valid():
            context["form"] = form
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            visibility = form.cleaned_data['visibility']

            try:
                username_db = User.objects.get(username__iexact=username)
                form.add_error(None, "Username already exists")
            except User.DoesNotExist:
                user = User.objects.create_user(username=username,
                                                password=password,
                                                email=email)
                new_user = authenticate(username=username,
                                        password=password)
                profile = Profile(user=user,
                                  visibility=visibility)
                profile.save()

                if new_user is not None:
                    login(request, new_user)
                    return HttpResponseRedirect(reverse('index'))
        else:
            form.add_error(None, "Something wrong happened")
        return render(request, 'registration/registration_form.html', context)
    else:
        form = forms.RegistrationForm()
        context["form"] = form

    return render(request, 'registration/registration_form.html', context)

def guide(request):
    context = {'page_title': 'guide'}
    return render(request, 'guide.html', context)

# API ---------------------------------

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
    mark = Bookmark.objects.get(id=id)
    if mark.user == request.user:
        mark.delete()

    if request.method == 'POST':
        return HttpResponse('success')

@login_required
def api_bump_mark(request, id):
    if mark.user == request.user:
        mark = get_object_or_404(Bookmark, id=id)
        mark.date_added = now()
        mark.save()

    if request.method == 'POST':
        return HttpResponse('success')
