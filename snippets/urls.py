from django.conf.urls import url
from snippets import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^snippets/$', views.SnippetList.as_view()),
    url(r'^snippets/(?P<pk>[0-9]+)/$',views.SnippetDetail.as_view()),
    url(r'^snip/(?P<pk>[0-9]+)/$', views.snippet_detail1,),
]
urlpatterns = format_suffix_patterns(urlpatterns)