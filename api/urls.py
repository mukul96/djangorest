# api/urls.py

from django.conf.urls import url,include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import CreateView
from rest import views

urlpatterns = {
    url(r'^bucketlists/$', CreateView.as_view(), name="create"),
    url(r'^users/', views.UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
}

urlpatterns = format_suffix_patterns(urlpatterns)