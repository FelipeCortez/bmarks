from django.test import TestCase
from marksapp.models import Tag, Bookmark
import marksapp.views as views

class FirstTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Tag.objects.create(name="music")
        Tag.objects.create(name="compsci")

    def test_one(self):
        music_tag = Tag.objects.get(id=1)
        #compsci_tag = Tag.objects.get(id=2)
        self.assertEquals(music_tag.name, "music")

    def test_split(self):
        strs_to_test = [
            "music, compsci, art",
            " music, compsci art",
            "music, compsci,art ",
            " music,compsci,   art",
            " music, compsci,,,art"]

        for string in strs_to_test:
            self.assertEquals(views.tags_strip_split(string), ["music", "compsci", "art"])
