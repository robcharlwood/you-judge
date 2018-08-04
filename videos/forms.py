from django import forms
from django.forms import formset_factory


class YouTubeVideoSearchForm(forms.Form):
    """
    Form to handle the querying of YouTube
    """
    keywords = forms.CharField(max_length=100)


class YouTubeVideoForm(forms.Form):
    """
    Form representing a single video response from the YouTube search. This
    form is used as part of the YouTubeVideoFormSet which allows us to add
    videos to a project in bulk
    """
    add = forms.BooleanField(label="", initial=False, required=False)
    youtube_id = forms.CharField(max_length=25, widget=forms.HiddenInput())
    name = forms.CharField(max_length=255, widget=forms.HiddenInput())
    description = forms.CharField(
        label="", required=False, widget=forms.Textarea(attrs={'hidden': ''}))
    published = forms.DateTimeField(widget=forms.HiddenInput())
    thumbnail_default = forms.CharField(
        max_length=255, widget=forms.HiddenInput())
    thumbnail_medium = forms.CharField(
        max_length=255, widget=forms.HiddenInput())
    thumbnail_high = forms.CharField(
        max_length=255, widget=forms.HiddenInput())


YouTubeVideoFormSet = formset_factory(YouTubeVideoForm, extra=0)
