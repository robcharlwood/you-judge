from django.conf.urls import url

from .views import (
    DashboardView,
    ProjectCreateView,
    ProjectDetailView,
    ProjectUpdateView,
    VideoAddView,
    VideoCommentListView,
    VideoDetailView,
    VideoSearchView,
    VideoTranscriptView
)

urlpatterns = (
    url(r'^$',  DashboardView.as_view(), name='dashboard'),
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
    url(r'^project/(?P<project_pk>\d+)/video/(?P<pk>\d+)/analysis/comments/$',
        VideoCommentListView.as_view(), name='video_comment_view'),
    url(r'^project/(?P<project_pk>\d+)/video/(?P<pk>\d+)/analysis/transcript/$',
        VideoTranscriptView.as_view(), name='video_transcript_view'),
)
