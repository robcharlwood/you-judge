from djangae.fields import JSONField
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save

from projects.models import Project
from .signals import import_youtube_comments


class Video(models.Model):
    """
    Represents a video within a project
    """
    owner = models.ForeignKey(get_user_model())
    project = models.ForeignKey(Project)
    # overall video sentiment analysis
    sentiment = models.IntegerField(default=0)
    magnitude = models.PositiveIntegerField(default=0)
    analyzed_transcript = JSONField(blank=True, null=True)
    # you tube specific data
    youtube_id = models.CharField(max_length=25)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    transcript = models.TextField(blank=True)
    published = models.DateTimeField()

    def __unicode__(self):
        return u'{}'.format(self.name)


class VideoComment(models.Model):
    """
    Represents a user's comment on a Video
    """
    video = models.ForeignKey(Video)
    # overall comment sentiment analysis
    sentiment = models.IntegerField(default=0)
    magnitude = models.PositiveIntegerField(default=0)
    analyzed_comment = JSONField(blank=True, null=True)
    # you tube specific data
    youtube_id = models.CharField(max_length=100)
    author_display_name = models.CharField(max_length=100)
    author_profile_image_url = models.CharField(max_length=255)
    comment_raw = models.TextField()
    comment_rich = models.TextField()
    published = models.DateTimeField()
    updated = models.DateTimeField()

    def __unicode__(self):
        return u'Video: {} Comment: {}'.format(self.video_id, self.comment_raw)


# connect up signal handling
post_save.connect(
    import_youtube_comments, sender=Video,
    dispatch_uid='import_youtube_comments')
