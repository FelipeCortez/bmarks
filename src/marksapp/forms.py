from django import forms
from django.forms import ModelForm, CharField, ChoiceField
from django.utils.safestring import mark_safe
from django.forms.utils import flatatt
from django.contrib.auth.models import User
from marksapp.models import Bookmark, Tag, Profile
import marksapp.views
import re

EMAIL_PLACEHOLDER_STR = 'optional! just in case you forget your password'

# https://github.com/wagtail/wagtail/issues/130#issuecomment-37180123
# fucking colons...
# hey maybe https://experiencehq.net/blog/better-django-modelform-html for placeholders
class BaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')  # globally override the Django >=1.6 default of ':'
        super(BaseForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                field.widget.attrs.update({
                    #'placeholder': field.label
                })

class BaseModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')  # globally override the Django >=1.6 default of ':'
        super(BaseModelForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                field.widget.attrs.update({
                    #'placeholder': field.label
                })


#http://stackoverflow.com/questions/4960445/display-a-comma-separated-list-of-manytomany-items-in-a-charfield-on-a-modelform
#http://pastebin.com/uvPL8Aat
class CommaTags(forms.Widget):
    # this is an awful way to do this
    # but I can't understand how django's widgets work so it will have to do for now
    def render(self, name, value, attrs=None):
        if attrs:
            attrs['autocomplete'] = 'off'
        final_attrs = self.build_attrs(attrs, type='text', name=name)
        objects = []

        if value is not None:
            if type(value) is not str:
                for each in value:
                    objects.append(each)
            else:
                objects = marksapp.views.tags_strip_split(value)

        values = []
        for each in objects:
            values.append(str(each))

        value = ', '.join(values)
        final_attrs['value'] = value
        return mark_safe(u'<input%s />' % flatatt(final_attrs))

class BookmarkForm(BaseModelForm):
    tags = CharField(widget=CommaTags)

    class Meta:
        model = Bookmark
        fields = ['url', 'name', 'tags', 'description']
        widgets = {
                'description': forms.Textarea(attrs={'rows':3, 'placeholder':'optional'}),
        }

    def save(self, commit=True, *args, **kwargs):
        m = super(BookmarkForm, self).save(commit=False, *args, **kwargs)
        form_tags = marksapp.views.tags_strip_split(self.cleaned_data['tags'])
        m.save()
        self.instance.tags.clear()

        for tag in form_tags:
            # optional dot, word characters, hyphens allowed
            if re.match("^\.?[-\w]+$", tag):
                t = Tag.objects.get_or_create(name=tag)[0]
                m.tags.add(t)
            else:
                print("WRONG")
        print(self.instance.tags)
        return m

class TagForm(BaseModelForm):
    class Meta:
        model = Tag
        fields = ['name']

    def is_valid(self):
        valid = super(TagForm, self).is_valid()

        if not valid:
            for f_name in self.errors:
                print(f_name)
            return valid

        return True

class RegistrationForm(BaseForm):
    username = CharField(label='Username', required=True)
    password = CharField(label='Password', required=True,
                         widget=forms.PasswordInput)
    email = CharField(label='E-mail',
                      required=False,
                      widget=forms.TextInput(attrs={'placeholder': EMAIL_PLACEHOLDER_STR}))
    visibility = ChoiceField(choices=Profile.visibility_choices,
                             label='Default visibility',
                             initial='PB',
                             widget=forms.RadioSelect())

class ProfileForm(BaseModelForm):
    class Meta:
        model = Profile
        fields = ['visibility']
        widgets = {
            'visibility': forms.RadioSelect(),
        }

class UserForm(BaseModelForm):
    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.TextInput(attrs={'placeholder': EMAIL_PLACEHOLDER_STR})
        }

class NetscapeForm(forms.Form):
    file = forms.FileField()

class ImportJsonForm(forms.Form):
    file = forms.FileField()
