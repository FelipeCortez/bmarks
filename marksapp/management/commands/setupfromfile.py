from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from marksapp.models import Bookmark, Tag
from html.parser import HTMLParser
import datetime

class NetscapeParser(HTMLParser):
    add_mark = False
    add_cat = False
    add_date = 0
    icon = ""
    href = ""
    tags = []
    categories = []
    bookmarks = []

    def handle_starttag(self, tag, attrs):
        if(tag == "h3"):
            self.add_cat = True
        if(tag == "a"):
            self.add_mark = True
            for attr in attrs:
                if attr[0] == "href":
                    self.href = attr[1]
                elif attr[0] == "add_date":
                    self.add_date = datetime.datetime.utcfromtimestamp(int(attr[1])).replace(tzinfo=datetime.timezone.utc)
                elif attr[0] == "icon":
                    self.icon = attr[1]
                elif attr[0] == "tags":
                    self.tags = attr[1].split(",")

    def handle_endtag(self, tag):
        if(tag == "dl"):
            if self.categories:
                self.categories.pop()

    def handle_data(self, data):
        if self.add_cat == True:
            self.categories.append(data.lower())
            self.add_cat = False
        elif self.add_mark == True:
            mark = {}
            mark["name"] = data
            mark["url"] = self.href
            mark["categories"] = self.categories[:]
            mark["tags"] = self.tags[:]
            mark["add_date"] = self.add_date
            self.bookmarks.append(mark)
            self.tags = []
            self.add_mark = False

def bookmarks_from_file(filename):
    with open(filename, 'r') as f:
        bookmarks = f.read()

        parser = NetscapeParser()
        parser.feed(bookmarks)
        return parser.bookmarks

class Command(BaseCommand):
    help = 'Populate DB from a Netscape bookmark file'

    def add_arguments(self, parser):
        parser.add_argument('filename')

    def handle(self, *args, **options):
        Bookmark.objects.all().delete()
        Tag.objects.all().delete()

        for mark in bookmarks_from_file(options["filename"]):
            b = Bookmark.objects.update_or_create(url=mark["url"])[0]
            b.name = mark["name"]
            b.date_added = mark["add_date"]

            for tag in mark["categories"] + mark["tags"]:
                t = Tag.objects.get_or_create(name=slugify(tag))[0]
                b.tags.add(t)

            b.save()

        print(Bookmark.objects.all())

        #b1 = Bookmark(name="Opa",
        #              url="opa.com")
        #b2 = Bookmark(name="Bicho",
        #              url="bicho.com")
        #b2.save()

        #t1 = Tag(name="inutil")
        #t2 = Tag(name="util")
        #t3 = Tag(name="teste")
        #b1.save()
        #t1.save()
        #t2.save()
        #t3.save()
        #b1.tags.add(t1)
        #b1.save()
        #b2.tags.add(t2)
        #b2.tags.add(t3)
        #b2.save()

        #print(b1)
        #print(b2)
