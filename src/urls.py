from django.conf.urls import include, url
from django.contrib import admin
from django.shortcuts import get_object_or_404, get_list_or_404
from django.db.models import Count
from marksapp.models import Bookmark, Tag
#from rest_framework import routers, serializers, viewsets
#from rest_framework.response import Response
#from rest_framework.decorators import detail_route, list_route

#class BookmarkSerializer(serializers.ModelSerializer):
#    tags = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Tag.objects.all())
#
#    class Meta:
#        model = Bookmark
#        fields = ('name', 'url', 'tags',)
#
#class TagSerializer(serializers.ModelSerializer):
#    count = serializers.SerializerMethodField()
#
#    def get_count(self, obj):
#        tag = Tag.objects.filter(name=obj.name)
#        count = Bookmark.objects.filter(tags=tag).count()
#        return count
#
#    class Meta:
#        model = Tag
#        fields = ('name', 'count')
#        lookup_field = 'name'
#
#class BookmarkViewSet(viewsets.ModelViewSet):
#    queryset = Bookmark.objects.all()
#    serializer_class = BookmarkSerializer
#
#    #def create(self, request):
#    #    mark = self.get_object()
#    #    serializer = BookmarkSerializer(data=request.data)
#    #    if serializer.is_valid():
#    #        mark.save()
#    #        return Response({'status': 'what....'})
#    #    else:
#    #        return Response(serializer.errors,
#    #                        status=status.HTTP_400_BAD_REQUEST)
#
#class TagViewSet(viewsets.ModelViewSet):
#    queryset = Tag.objects.all()
#    serializer_class = TagSerializer
#    lookup_field = 'name'
#
#    def list(self, request):
#        top_tags = Tag.objects.all() \
#                              .annotate(num_marks=Count('bookmark')) \
#                              .order_by('-num_marks')
#        serializer = TagSerializer(top_tags, many=True)
#        return Response(serializer.data)
#
#
#    def retrieve(self, request, pk=None, name=None):
#        tag_query = Tag.objects.filter(name=name)
#        queryset = Bookmark.objects.filter(tags=tag_query)
#        serializer = BookmarkSerializer(queryset, many=True)
#        return Response(serializer.data)
#
#    #def create(self, request):
#    #    mark = self.get_object()
#    #    serializer = BookmarkSerializer(data=request.data)
#    #    if serializer.is_valid():
#    #        mark.save()
#    #        return Response({'status': 'what....'})
#    #    else:
#    #        return Response(serializer.errors,
#    #                        status=status.HTTP_400_BAD_REQUEST)
#
#router = routers.DefaultRouter()
#router.register(r'bookmarks', BookmarkViewSet)
#router.register(r'tags', TagViewSet)

urlpatterns = [
    #url(r'^api/', include(router.urls)),
    url(r'^', include('marksapp.urls')),
    url(r'^admin/', admin.site.urls),
]
