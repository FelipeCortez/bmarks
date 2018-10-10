from django import template
from django.template.defaultfilters import stringfilter
import markdown as mdown # sorry

register = template.Library()

@register.filter(name='remove_tag')
def remove_tag(value, tag):
    tags = value[:]
    tags.remove(tag)
    return "+".join(tags)

@register.filter(name='add_tag')
def add_tag(value, new_tag):
    tags = value[:]
    tags.append(new_tag)
    return "+".join(tags)

@register.filter(name='markdown')
@stringfilter
def markdown(value):
    return mdown.markdown(value)
