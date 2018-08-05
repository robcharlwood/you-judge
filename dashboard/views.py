import datetime

from djangae.contrib.consistency import improve_queryset_consistency
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.list import ListView

from projects.forms import ProjectForm
from projects.models import Project
from services import youtube
from videos.forms import YouTubeVideoFormSet, YouTubeVideoSearchForm
from videos.models import Video, VideoComment


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        try:
            self.pre_checks()
        except AttributeError:
            pass
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class DashboardView(LoginRequiredMixin, ListView):
    """
    Dashboard - Home view (lists all projects)
    """
    model = Project
    template_name = 'dashboard.html'

    def get_queryset(self):
        return improve_queryset_consistency(
            self.model.objects.filter(owner=self.request.user))


class ProjectCreateView(LoginRequiredMixin, CreateView):
    """
    Allows users to create a project
    """
    template_name = 'project_create.html'
    form_class = ProjectForm
    model = Project

    def get_success_url(self):
        return reverse('dashboard:dashboard')

    def form_valid(self, form):
        messages.success(self.request, 'Project created succesfully!')
        instance = form.save(commit=False)
        instance.owner = self.request.user
        instance.save()
        return super(ProjectCreateView, self).form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    """
    Allows users to update a project
    """
    template_name = 'project_update.html'
    form_class = ProjectForm
    model = Project

    def get_success_url(self):
        return reverse('dashboard:dashboard')

    def get_queryset(self):
        return improve_queryset_consistency(
            self.model.objects.filter(owner=self.request.user))

    def form_valid(self, form):
        messages.success(self.request, 'Project updated succesfully!')
        form.save()
        return super(ProjectUpdateView, self).form_valid(form)


class ProjectDetailView(LoginRequiredMixin, DetailView):
    """
    Allows users to view a project
    """
    template_name = 'project_detail.html'
    model = Project

    def get_queryset(self):
        return improve_queryset_consistency(
            self.model.objects.filter(owner=self.request.user))

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        context['video_search_form'] = YouTubeVideoSearchForm()
        context['videos'] = improve_queryset_consistency(
            self.object.video_set.all())
        return context


class VideoSearchView(LoginRequiredMixin, FormView):
    """
    Allows users to search youtube for videos to add to their project
    """
    template_name = 'video_search_results.html'
    form_class = YouTubeVideoSearchForm

    def get(self, request, pk):
        return HttpResponseNotAllowed('post')

    def get_context_data(self, form, **kwargs):
        context = super(VideoSearchView, self).get_context_data(**kwargs)
        project = get_object_or_404(
            Project, pk=self.kwargs['pk'], owner=self.request.user)
        results = youtube.Client().search(form.cleaned_data.get('keywords'))
        existing_videos = [v.youtube_id for v in Video.objects.filter(
            project__pk=project.pk)]
        context['project'] = project

        # remove videos already added to project from results
        for i, r in enumerate(results):
            if r['id'] in existing_videos:
                results.pop(i)

        # construct a formset with the rest of the results data
        context['formset'] = YouTubeVideoFormSet(initial=[{
            'youtube_id': result['id'],
            'published': datetime.datetime.strptime(
                result['snippet']['publishedAt'],
                "%Y-%m-%dT%H:%M:%S.%fZ"),
            'name': result['snippet']['title'],
            'description': result['snippet']['description'],
            'thumbnail_default':
                result['snippet']['thumbnails']['default']['url'],
            'thumbnail_medium':
                result['snippet']['thumbnails']['medium']['url'],
            'thumbnail_high':
                result['snippet']['thumbnails']['high']['url'],
            'likes': result['statistics'].get('likeCount', 0),
            'dislikes': result['statistics'].get('dislikeCount', 0),
            'comment_count': result['statistics'].get('commentCount', 0),
            }
            for result in results
        ])
        return context

    def form_valid(self, form):
        return self.render_to_response(self.get_context_data(form))


class VideoAddView(LoginRequiredMixin, View):
    def post(self, request, pk):
        """
        POST only view that validates the formset from the video search view
        and creates video objects for each item added.
        """
        project = get_object_or_404(
            Project, pk=pk, owner=self.request.user)
        formset = YouTubeVideoFormSet(request.POST, request.FILES)
        if formset.is_valid():
            messages.success(request, 'Videos added succesfully!')
            for form in formset:
                if form.cleaned_data.get('add', None):
                    Video.objects.create(
                        owner=self.request.user,
                        project=project,
                        youtube_id=form.cleaned_data['youtube_id'],
                        name=form.cleaned_data['name'],
                        published=form.cleaned_data['published'],
                        description=form.cleaned_data['description'],
                        thumbnail_default=form.cleaned_data['thumbnail_default'],
                        thumbnail_medium=form.cleaned_data['thumbnail_medium'],
                        thumbnail_high=form.cleaned_data['thumbnail_high'],
                        likes=form.cleaned_data['likes'],
                        dislikes=form.cleaned_data['dislikes'],
                        comment_count=form.cleaned_data['comment_count'])
        return HttpResponseRedirect(reverse(
            'dashboard:project_view', kwargs={'pk': project.pk}))


class VideoDetailView(LoginRequiredMixin, DetailView):
    """
    Allows users to view a project
    """
    template_name = 'video_detail.html'
    model = Video

    def get_queryset(self):
        return improve_queryset_consistency(
            self.model.objects.filter(
                project=self.kwargs['project_pk'], owner=self.request.user))


class VideoCommentListView(LoginRequiredMixin, ListView):
    model = VideoComment
    template_name = 'video_comments.html'

    def get_queryset(self):
        return improve_queryset_consistency(
            self.model.objects.filter(video=self.video))

    def pre_checks(self):
        """
        Ensures relevant objects exist and that the current user is the owner
        """
        self.project = get_object_or_404(
            Project, pk=self.kwargs['project_pk'], owner=self.request.user)
        self.video = get_object_or_404(
            Video, pk=self.kwargs['pk'], project=self.project)

    def get_context_data(self, **kwargs):
        context = super(VideoCommentListView, self).get_context_data(**kwargs)
        context['project'] = self.project
        context['video'] = self.video
        return context


class VideoTranscriptView(LoginRequiredMixin, DetailView):
    """
    Allows users to view a project
    """
    template_name = 'video_transcript.html'
    model = Video

    def get_queryset(self):
        return improve_queryset_consistency(
            self.model.objects.filter(
                project=self.kwargs['project_pk'], owner=self.request.user))
