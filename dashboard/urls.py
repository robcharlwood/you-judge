from django.conf.urls import url

from .views import (
    DashboardView,
    HomeView,
    ProjectCreateView,
    ProjectDetailView,
    ProjectUpdateView,
    VideoAddView,
    VideoDetailView,
    VideoSearchView
)

urlpatterns = (
    url(r'^$',  HomeView.as_view(), name='home'),
    url(r'^dashboard/$',  DashboardView.as_view(), name='dashboard'),
    url(r'^project/new/$',
        ProjectCreateView.as_view(), name='project_create'),
    url(r'^project/view/(?P<pk>\d+)/$',
        ProjectDetailView.as_view(), name='project_view'),
    url(r'^project/edit/(?P<pk>\d+)/$',
        ProjectUpdateView.as_view(), name='project_update'),
    url(r'^project/(?P<pk>\d+)/video/search/$',
        VideoSearchView.as_view(), name='video_search'),
    url(r'^project/(?P<pk>\d+)/video/search/add/$',
        VideoAddView.as_view(), name='video_add'),
    url(r'^project/(?P<project_pk>\d+)/video/view/(?P<pk>\d+)/$',
        VideoDetailView.as_view(), name='video_view'),
)
