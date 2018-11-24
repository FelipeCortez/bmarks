from django.test import TestCase
from django.contrib.auth.models import User
from marksapp.models import Tag, Bookmark
import marksapp.views as views


def marks_names(marks):
    return [m.name for m in marks]


class PaginateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='testuser')

        for i in range(1, 12):
            Bookmark.objects.create(name=f"b{i}", date_added="2018-11-02")

    def test_first_page(self):
        result = views.paginate(Bookmark.objects, limit = 3)
        self.assertEqual(marks_names(result["marks"]), ["b11", "b10", "b9"])
        self.assertEqual(result["after_link"].name, "b9")
        self.assertIs(result["before_link"], None)

    def test_transition(self):
        first_page = views.paginate(Bookmark.objects, limit = 3)
        after_first = first_page["after_link"]
        second_page = views.paginate(Bookmark.objects, after = after_first, limit = 3)

        self.assertEqual(marks_names(second_page["marks"]), ["b8", "b7", "b6"])
        self.assertEqual(second_page["after_link"].name, "b6")
        self.assertEqual(second_page["before_link"].name, "b8")

    def test_after(self):
        b7 = Bookmark.objects.get(name="b7")
        result = views.paginate(Bookmark.objects, after = b7, limit = 3)

        self.assertEqual(marks_names(result["marks"]), ["b6", "b5", "b4"])
        self.assertEqual(result["after_link"].name, "b4")
        self.assertEqual(result["before_link"].name, "b6")

    def test_before(self):
        b6 = Bookmark.objects.get(name="b6")
        result = views.paginate(Bookmark.objects, before = b6, limit = 3)

        self.assertEqual(marks_names(result["marks"]), ["b9", "b8", "b7"])
        self.assertEqual(result["after_link"].name, "b7")
        self.assertEqual(result["before_link"].name, "b9")

    def test_incomplete_last_page(self):
        b3 = Bookmark.objects.get(name="b3")
        result = views.paginate(Bookmark.objects, after = b3, limit = 3)

        self.assertEqual(marks_names(result["marks"]), ["b2", "b1"])
        self.assertIs(result["after_link"], None)
        self.assertEqual(result["before_link"].name, "b2")

    def test_pagination_by_name(self):
        result = views.paginate(Bookmark.objects, limit = 5, sort_column = "name")

        self.assertEqual(marks_names(result["marks"]), ["b1", "b10", "b11", "b2", "b3"])
        self.assertEqual(result["after_link"].name, "b3")
        self.assertIs(result["before_link"], None)

    def test_pagination_by_name_inverse(self):
        result = views.paginate(Bookmark.objects, limit = 5, sort_column = "-name")

        self.assertEqual(marks_names(result["marks"]), ["b9", "b8", "b7", "b6", "b5"])
        self.assertEqual(result["after_link"].name, "b5")
        self.assertIs(result["before_link"], None)
