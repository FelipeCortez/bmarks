from django.test import TestCase
from django.contrib.auth.models import User
from marksapp.models import Tag, Bookmark
from marksapp.misc import tag_regex, multitag_regex, website_from_url
import marksapp.views as views
import re


class WebsiteFromURL(TestCase):
    @classmethod
    def setUpTestData(cls):
        Tag.objects.create(name="music")
        Tag.objects.create(name="compsci")

    def test_extract(self):
        strs_to_test = {
            "https://bmarks.net": "bmarks.net",
            "http://bmarks.net": "bmarks.net",
            "ftp://bmarks.net": "bmarks.net",
            "bmarks.net": "bmarks.net",
            "www.bmarks.net": "bmarks.net",
            "www.bmarks.net/": "bmarks.net",
            "www.bmarks.net/etc": "bmarks.net",
            # "subdomain.bmarks.net/etc" : "bmarks.net",
            # "iamnotadomain" : None,
        }

        for url, expected in strs_to_test.items():
            self.assertEquals(expected, website_from_url(url))


class TagSplitTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Tag.objects.create(name="music")
        Tag.objects.create(name="compsci")

    def test_creation(self):
        music_tag = Tag.objects.get(id=1)
        self.assertEquals(music_tag.name, "music")

    def test_split(self):
        strs_to_test = [
            "music, compsci, art",
            " music, compsci art",
            "music, compsci,art ",
            " music,compsci,   art",
            " music, compsci,,,art",
            "music, compsci, art",
            "music compsci art",
        ]

        for string in strs_to_test:
            self.assertEquals(
                views.tags_strip_split(string), ["music", "compsci", "art"]
            )


class RegexTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def test_simple(self):
        tag_simple = ".unlisted"
        assert re.match(tag_regex, tag_simple) is not None

    def test_multi(self):
        multi_tags = [
            "compsci",
            ".unlisted",
            ".unlisted+compsci",
            ".unlisted+.notreallylisted",
            "very+normal+indeed",
        ]

        for string in multi_tags:
            assert re.match(multitag_regex, string) is not None
