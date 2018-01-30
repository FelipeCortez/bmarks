from django import forms
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import validate_slug

class Tag(models.Model):
    name = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Bookmark(models.Model):
    name = models.CharField(max_length=128)
    url = models.CharField(max_length=512, blank=True)
    description = models.TextField(blank=True)
    date_added = models.DateTimeField('date added', default=timezone.now)
    tags = models.ManyToManyField(Tag)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    def tags_str(self):
        return ", ".join(t.name for t in self.tags.all())

    def __str__(self):
        return "{}\n{}\n[{}]\n<{}>\n---\n".format(self.user.username, self.name, self.url, self.tags_str())

