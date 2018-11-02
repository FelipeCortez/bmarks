from django.test import TestCase
from django.contrib.auth.models import User
from marksapp.models import Tag, Bookmark
from marksapp.misc import tag_regex, multitag_regex, websiteFromURL
import marksapp.views as views
import re

class WebsiteFromURL(TestCase):
    @classmethod
    def setUpTestData(cls):
        Tag.objects.create(name="music")
        Tag.objects.create(name="compsci")

    def test_extract(self):
        strs_to_test = {
            "https://bmarks.net" : "bmarks.net",
            "http://bmarks.net"  : "bmarks.net",
            "ftp://bmarks.net"   : "bmarks.net",
            "bmarks.net"         : "bmarks.net",
            "www.bmarks.net"     : "bmarks.net",
            "www.bmarks.net/"    : "bmarks.net",
            "www.bmarks.net/etc" : "bmarks.net",
            "subdomain.bmarks.net/etc" : "bmarks.net",
            "iamnotadomain" : None,
        }

        for url, expected in strs_to_test.items():
            print(url, websiteFromURL(url))
            # self.assertEquals(
            #     views.tags_strip_split(string), ["music", "compsci", "art"])


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
                views.tags_strip_split(string), ["music", "compsci", "art"])

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

class PaginateTests(TestCase):
    """
    ---
    1. One
    1. Two
    1. Three
    1. ---
    1. Four
    2. Five
    2. Six
    2. ---
    2. Seven
    2. Eight
    2. Nine
    2. ---
    2. Ten
    2. Eleven
    """

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='testuser')

        for i in range(1, 12):
            Bookmark.objects.create(name=f"b{i}", date_added="2018-11-02")

    def test_first_page(self):
        result = views.paginate(Bookmark.objects, limit = 3)
        self.assertEqual(result["paginated_marks"], ["b11", "b10", "b9"])
        self.assertEqual(result["after_link"].name, "b9")
        self.assertIs(result["before_link"], None)

    def test_transition(self):
        first_page = views.paginate(Bookmark.objects, limit = 3)
        after_first = first_page["after_link"]
        second_page = views.paginate(Bookmark.objects, after = after_first, limit = 3)

        self.assertEqual(second_page["paginated_marks"], ["b8", "b7", "b6"])
        self.assertEqual(second_page["after_link"].name, "b6")
        self.assertEqual(second_page["before_link"].name, "b8")

    def test_after(self):
        b7 = Bookmark.objects.get(name="b7")
        result = views.paginate(Bookmark.objects, after = b7, limit = 3)

        self.assertEqual(result["paginated_marks"], ["b6", "b5", "b4"])
        self.assertEqual(result["after_link"].name, "b4")
        self.assertEqual(result["before_link"].name, "b6")

    def test_before(self):
        b6 = Bookmark.objects.get(name="b6")
        result = views.paginate(Bookmark.objects, before = b6, limit = 3)

        self.assertEqual(result["paginated_marks"], ["b9", "b8", "b7"])
        self.assertEqual(result["after_link"].name, "b7")
        self.assertEqual(result["before_link"].name, "b9")

    def test_incomplete_last_page(self):
        b3 = Bookmark.objects.get(name="b3")
        result = views.paginate(Bookmark.objects, after = b3, limit = 3)

        self.assertEqual(result["paginated_marks"], ["b2", "b1"])
        self.assertIs(result["after_link"], None)
        self.assertEqual(result["before_link"].name, "b2")
