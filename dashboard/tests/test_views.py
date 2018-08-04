from djangae.test import TestCase
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from django.http import Http404
from django.test import RequestFactory

import mock

from core.tests.factories import (
    AuthenticatedUserFactory,
    ProjectFactory,
    VideoFactory
)
from dashboard.views import (
    DashboardView,
    HomeView,
    ProjectCreateView,
    ProjectDetailView,
    ProjectUpdateView,
    VideoAddView,
    VideoDetailView,
    VideoSearchView
)


class HomeViewTestCase(TestCase):
    def setUp(self):
        super(HomeViewTestCase, self).setUp()
        self.rf = RequestFactory()

    def test_200_ok_anon(self):
        request = self.rf.get('/')
        request.user = AnonymousUser()
        resp = HomeView.as_view()(request)
        self.assertEqual(resp.status_code, 200)

    def test_200_ok_logged_in(self):
        request = self.rf.get('/')
        request.user = AuthenticatedUserFactory()
        resp = HomeView.as_view()(request)
        self.assertEqual(resp.status_code, 200)


class DashboardViewTestCase(TestCase):
    def setUp(self):
        super(DashboardViewTestCase, self).setUp()
        self.rf = RequestFactory()

    def test_302_not_logged_in(self):
        request = self.rf.get('/dashboard/')
        request.user = AnonymousUser()
        resp = DashboardView.as_view()(request)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp._headers['location'][1], '/accounts/login/?next=/dashboard/')

    def test_200_ok(self):
        # check 200 and that user can only see their projects
        logged_in_user = AuthenticatedUserFactory()
        other_user_project = ProjectFactory()
        logged_in_project = ProjectFactory(owner=logged_in_user)
        request = self.rf.get('/dashboard/')
        request.user = logged_in_user
        resp = DashboardView.as_view()(request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context_data['object_list']), 1)
        self.assertEqual(
            resp.context_data['object_list'][0].pk, logged_in_project.pk)
        self.assertNotEqual(
            resp.context_data['object_list'][0].pk, other_user_project.pk)


class ProjectDetailViewTestCase(TestCase):
    def setUp(self):
        super(ProjectDetailViewTestCase, self).setUp()
        self.rf = RequestFactory()

    def test_302_not_logged_in(self):
        project = ProjectFactory()
        request = self.rf.get('/project/view/{}'.format(project.pk))
        request.user = AnonymousUser()
        resp = ProjectDetailView.as_view()(request, pk=project.pk)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp._headers['location'][1],
            '/accounts/login/?next=/project/view/{}'.format(project.pk))

    def test_404_logged_in_permission_denied(self):
        # users cant see the details of a project they dont own
        project = ProjectFactory()
        logged_in_user = AuthenticatedUserFactory()
        request = self.rf.get('/project/view/{}'.format(project.pk))
        request.user = logged_in_user
        with self.assertRaises(Http404):
            ProjectDetailView.as_view()(request, pk=project.pk)

    def test_200_ok_logged_in(self):
        logged_in_user = AuthenticatedUserFactory()
        project = ProjectFactory(owner=logged_in_user)
        request = self.rf.get('/project/view/{}'.format(project.pk))
        request.user = logged_in_user
        resp = ProjectDetailView.as_view()(request, pk=project.pk)
        self.assertEqual(200, resp.status_code)


class ProjectCreateViewTestCase(TestCase):
    def setUp(self):
        super(ProjectCreateViewTestCase, self).setUp()
        self.rf = RequestFactory()

    def test_get_302_not_logged_in(self):
        request = self.rf.get('/project/new/')
        request.user = AnonymousUser()
        resp = ProjectCreateView.as_view()(request)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp._headers['location'][1],
            '/accounts/login/?next=/project/new/')

    def test_post_302_not_logged_in(self):
        request = self.rf.post('/project/new/', {'name': 'Foo'})
        request.user = AnonymousUser()
        resp = ProjectCreateView.as_view()(request)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp._headers['location'][1],
            '/accounts/login/?next=/project/new/')

    def test_get_200_ok_logged_in(self):
        logged_in_user = AuthenticatedUserFactory()
        request = self.rf.get('/project/view/new')
        request.user = logged_in_user
        resp = ProjectCreateView.as_view()(request)
        self.assertEqual(200, resp.status_code)

    @mock.patch('djangae.contrib.gauth.middleware.get_user')
    def test_post_302_ok_logged_in(self, mock_get_user):
        # successfully created project should redirect to dashboard
        logged_in_user = AuthenticatedUserFactory()
        mock_get_user.return_value = logged_in_user

        response = self.client.post(
            reverse('dashboard:project_create'), {
                'name': 'Foo',
            })

        self.assertEqual(302, response.status_code)
        self.assertEqual(
            response._headers['location'][1], '/dashboard/')
        project = ProjectFactory._meta.model.objects.get()
        self.assertEqual(project.name, 'Foo')
        self.assertEqual(project.owner, logged_in_user)


class ProjectUpdateViewTestCase(TestCase):
    def setUp(self):
        super(ProjectUpdateViewTestCase, self).setUp()
        self.rf = RequestFactory()

    def test_get_302_not_logged_in(self):
        project = ProjectFactory()
        request = self.rf.get('/project/edit/{}'.format(project.pk))
        request.user = AnonymousUser()
        resp = ProjectUpdateView.as_view()(request, pk=project.pk)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp._headers['location'][1],
            '/accounts/login/?next=/project/edit/{}'.format(project.pk))

    def test_post_302_not_logged_in(self):
        project = ProjectFactory()
        request = self.rf.post(
            '/project/edit/{}'.format(project.pk), {'name': 'Foo'})
        request.user = AnonymousUser()
        resp = ProjectUpdateView.as_view()(request, pk=project.pk)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp._headers['location'][1],
            '/accounts/login/?next=/project/edit/{}'.format(project.pk))

    def test_get_404_logged_in_permission_denied(self):
        project = ProjectFactory()
        logged_in_user = AuthenticatedUserFactory()
        request = self.rf.get('/project/edit/{}'.format(project.pk))
        request.user = logged_in_user
        with self.assertRaises(Http404):
            ProjectUpdateView.as_view()(request, pk=project.pk)

    def test_get_200_ok_logged_in(self):
        logged_in_user = AuthenticatedUserFactory()
        project = ProjectFactory(owner=logged_in_user)
        request = self.rf.get('/project/edit/{}'.format(project.pk))
        request.user = logged_in_user
        resp = ProjectUpdateView.as_view()(request, pk=project.pk)
        self.assertEqual(200, resp.status_code)

    @mock.patch('djangae.contrib.gauth.middleware.get_user')
    def test_post_302_ok_logged_in(self, mock_get_user):
        # successfully update project should redirect to dashboard
        logged_in_user = AuthenticatedUserFactory()
        project = ProjectFactory(owner=logged_in_user, name='Foo')
        mock_get_user.return_value = logged_in_user

        response = self.client.post(
            reverse('dashboard:project_update', kwargs={'pk': project.pk}), {
                'name': 'Bar',
            })

        self.assertEqual(302, response.status_code)
        self.assertEqual(
            response._headers['location'][1], '/dashboard/')
        project = ProjectFactory._meta.model.objects.get()
        self.assertEqual(project.name, 'Bar')
        self.assertEqual(project.owner, logged_in_user)


class VideoSearchViewTestCase(TestCase):
    def setUp(self):
        super(VideoSearchViewTestCase, self).setUp()
        self.rf = RequestFactory()

    def test_get_302_not_logged_in(self):
        # get on video search view should raise a 302
        project = ProjectFactory()
        request = self.rf.get('/project/{}/video/search'.format(project.pk))
        request.user = AnonymousUser()
        resp = VideoSearchView.as_view()(request, pk=project.pk)
        self.assertEqual(resp.status_code, 302)

    def test_get_405_logged_in(self):
        # get on video search view should raise a 405 when logged in
        project = ProjectFactory()
        request = self.rf.get('/project/{}/video/search'.format(project.pk))
        request.user = AuthenticatedUserFactory()
        resp = VideoSearchView.as_view()(request, pk=project.pk)
        self.assertEqual(resp.status_code, 405)

    def test_post_404_logged_in_permission_denied(self):
        # cant search for videos on a project thats not yours or doesnt exist
        project = ProjectFactory()
        request = self.rf.post('/project/{}/video/search'.format(project.pk), {
            'keywords': 'foo'
        })
        request.user = AuthenticatedUserFactory()
        with self.assertRaises(Http404):
            VideoSearchView.as_view()(request, pk=project.pk)

    def test_post_200_logged_in(self):
        mock_search_resp = [{
            u'snippet': {
                u'categoryId': u'25',
                u'channelId': u'channel1234',
                u'channelTitle': u'channel Title',
                u'description': u'video 1234 description',
                u'liveBroadcastContent': u'none',
                u'localized': {
                    u'description': u'description',
                    u'title': u'Video 1234'
                },
                u'publishedAt': u'2018-01-01T00:00:00.000Z',
                u'tags': [
                    u'tag1',
                    u'tag2',
                ],
                u'thumbnails': {
                    u'default': {
                        u'height': 90,
                        u'url': u'http://example.com/default.jpg',
                        u'width': 120
                    },
                    u'high': {
                        u'height': 360,
                        u'url': u'hhttp://example.com/high.jpg',
                        u'width': 480
                    },
                    u'maxres': {
                        u'height': 720,
                        u'url': u'http://example.com/maxres.jpg',
                        u'width': 1280
                    },
                    u'medium': {
                        u'height': 180,
                        u'url': u'http://example.com/medium.jpg',
                        u'width': 320
                    },
                    u'standard': {
                        u'height': 480,
                        u'url': u'http://example.com/standard.jpg',
                        u'width': 640
                    }
                },
                u'title': u'Video 1234'
            },
            u'statistics': {
                u'commentCount': u'9999',
                u'viewCount': u'9999',
                u'favoriteCount': u'9999',
                u'dislikeCount': u'9999',
                u'likeCount': u'9999'
            },
            u'kind': u'youtube#video',
            u'etag': u'"etag/123456789"',
            u'id': u'video1234'
        }, {
            u'snippet': {
                u'categoryId': u'25',
                u'channelId': u'channel5678',
                u'channelTitle': u'channel Title',
                u'description': u'video 5678 description',
                u'liveBroadcastContent': u'none',
                u'localized': {
                    u'description': u'description',
                    u'title': u'Video 5678'
                },
                u'publishedAt': u'2018-01-01T00:00:00.000Z',
                u'tags': [
                    u'tag1',
                    u'tag2',
                ],
                u'thumbnails': {
                    u'default': {
                        u'height': 90,
                        u'url': u'http://example.com/default.jpg',
                        u'width': 120
                    },
                    u'high': {
                        u'height': 360,
                        u'url': u'hhttp://example.com/high.jpg',
                        u'width': 480
                    },
                    u'maxres': {
                        u'height': 720,
                        u'url': u'http://example.com/maxres.jpg',
                        u'width': 1280
                    },
                    u'medium': {
                        u'height': 180,
                        u'url': u'http://example.com/medium.jpg',
                        u'width': 320
                    },
                    u'standard': {
                        u'height': 480,
                        u'url': u'http://example.com/standard.jpg',
                        u'width': 640
                    }
                },
                u'title': u'Video 5678'
            },
            u'statistics': {
                u'commentCount': u'9999',
                u'viewCount': u'9999',
                u'favoriteCount': u'9999',
                u'dislikeCount': u'9999',
                u'likeCount': u'9999'
            },
            u'kind': u'youtube#video',
            u'etag': u'"etag/123456789"',
            u'id': u'video5678'
        }]
        logged_in_user = AuthenticatedUserFactory()
        project = ProjectFactory(owner=logged_in_user)
        existing_video = VideoFactory(project=project, youtube_id='video5678')
        request = self.rf.post(
            '/project/{}/video/search'.format(project.pk),
            {'keywords': 'kittens'})
        request.user = logged_in_user
        service = mock.Mock()
        service.search.return_value = mock_search_resp
        with mock.patch('dashboard.views.youtube.Client') as mock_yt:
            mock_yt.return_value = service
            resp = VideoSearchView.as_view()(request, pk=project.pk)
            self.assertEqual(200, resp.status_code)
            self.assertEqual(1, len(resp.context_data['formset'].forms))
            self.assertEqual(
                'video1234',
                resp.context_data['formset'].forms[0].initial['youtube_id'])
            self.assertNotEqual(
                existing_video.youtube_id,
                resp.context_data['formset'].forms[0].initial['youtube_id'])


class VideoAddViewTestCase(TestCase):
    def setUp(self):
        super(VideoAddViewTestCase, self).setUp()
        self.rf = RequestFactory()

    def test_get_302_not_logged_in(self):
        # get on video search view should raise a 302
        project = ProjectFactory()
        request = self.rf.get(
            '/project/{}/video/search/add'.format(project.pk))
        request.user = AnonymousUser()
        resp = VideoAddView.as_view()(request, pk=project.pk)
        self.assertEqual(resp.status_code, 302)

    def test_get_405_logged_in(self):
        # get on video add view should raise a 405 when logged in
        project = ProjectFactory()
        request = self.rf.get(
            '/project/{}/video/search/add/'.format(project.pk))
        request.user = AuthenticatedUserFactory()
        resp = VideoAddView.as_view()(request, pk=project.pk)
        self.assertEqual(resp.status_code, 405)

    def test_post_404_logged_in_permission_denied(self):
        # cant add videos to a project thats not yours or doesnt exist
        project = ProjectFactory()
        request = self.rf.post(
            '/project/{}/video/search/add/'.format(project.pk), {})
        request.user = AuthenticatedUserFactory()
        with self.assertRaises(Http404):
            VideoAddView.as_view()(request, pk=project.pk)

    @mock.patch('djangae.contrib.gauth.middleware.get_user')
    def test_post_302_logged_in(self, mock_get_user):
        logged_in_user = AuthenticatedUserFactory()
        project = ProjectFactory(owner=logged_in_user)
        mock_get_user.return_value = logged_in_user

        response = self.client.post(
            reverse('dashboard:video_add', kwargs={'pk': project.pk}), {
                # management form data
                'form-TOTAL_FORMS': 2,
                'form-INITIAL_FORMS': 2,
                'form-MIN_NUM_FORMS': 0,
                'form-MAX_NUM_FORMS': 1000,
                # add these two
                'form-0-add': True,
                'form-0-youtube_id': 'video1234',
                'form-0-name': 'Video 1234',
                'form-0-published': '2018-05-16 15:30:00',
                'form-0-description': 'Video 1234 description',
                'form-0-thumbnail_default': 'http://example.com/default.jpg',
                'form-0-thumbnail_medium': 'http://example.com/medium.jpg',
                'form-0-thumbnail_high': 'http://example.com/high.jpg',
                'form-1-add': True,
                'form-1-youtube_id': 'video5678',
                'form-1-name': 'Video 5678',
                'form-1-published': '2018-05-16 15:30:00',
                'form-1-description': 'Video 5678 description',
                'form-1-thumbnail_default': 'http://example.com/default.jpg',
                'form-1-thumbnail_medium': 'http://example.com/medium.jpg',
                'form-1-thumbnail_high': 'http://example.com/high.jpg',
                # dont add this one
                'form-2-add': False,
                'form-2-youtube_id': 'video9999',
                'form-2-name': 'Video 9999',
                'form-2-published': '2018-05-16 15:30:00',
                'form-2-description': 'Video 9999 description',
                'form-2-thumbnail_default': 'http://example.com/default.jpg',
                'form-2-thumbnail_medium': 'http://example.com/medium.jpg',
                'form-2-thumbnail_high': 'http://example.com/high.jpg',
            })

        self.assertEqual(302, response.status_code)
        self.assertEqual(
            response._headers['location'][1],
            '/project/view/{}/'.format(project.pk))
        videos = VideoFactory._meta.model.objects.all()
        self.assertEqual(2, len(videos))
        video_ids = [v.youtube_id for v in videos]
        self.assertIn('video1234', video_ids)
        self.assertIn('video5678', video_ids)
        self.assertNotIn('video9999', video_ids)


class VideoDetailViewTestCase(TestCase):
    def setUp(self):
        super(VideoDetailViewTestCase, self).setUp()
        self.rf = RequestFactory()

    def test_302_not_logged_in(self):
        project = ProjectFactory()
        video = VideoFactory(project=project)
        request = self.rf.get(
            '/project/{}/video/view/{}'.format(project.pk, video.pk))
        request.user = AnonymousUser()
        resp = VideoDetailView.as_view()(
            request, project_pk=project.pk, pk=video.pk)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp._headers['location'][1],
            '/accounts/login/?next=/project/{}/video/view/{}'.format(
                project.pk, video.pk))

    def test_404_logged_in_permission_denied(self):
        # users cant see the details of a project they dont own
        project = ProjectFactory()
        video = VideoFactory(project=project)
        logged_in_user = AuthenticatedUserFactory()
        request = self.rf.get(
            '/project/{}/video/view/{}'.format(project.pk, video.pk))
        request.user = logged_in_user
        with self.assertRaises(Http404):
            VideoDetailView.as_view()(
                request, project_pk=project.pk, pk=video.pk)

    def test_200_ok_logged_in(self):
        logged_in_user = AuthenticatedUserFactory()
        project = ProjectFactory(owner=logged_in_user)
        video = VideoFactory(project=project, owner=logged_in_user)
        request = self.rf.get('/project/{}/video/view/{}'.format(
            project.pk, video.pk))
        request.user = logged_in_user
        resp = VideoDetailView.as_view()(
            request, project_pk=project.pk, pk=video.pk)
        self.assertEqual(200, resp.status_code)
