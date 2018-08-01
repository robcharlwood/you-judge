from djangae.fields import JSONField
from django.db import models

from projects.models import Project


class Video(models.Model):
    """
    Represents a video within a project
    """
    project = models.ForeignKey(Project)
    # overall video sentiment analysis
    sentiment = models.IntegerField(default=0)
    magnitude = models.PositiveIntegerField(default=0)
    analyzed_transcript = JSONField(blank=True, null=True)
    # you tube specific data
    name = models.CharField(max_length=255)
    description = models.TextField()
    published = models.DateTimeField()
    duration = models.CharField(max_length=25)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)

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
    author_display_name = models.CharField(max_length=100)
    author_profile_image_url = models.CharField(max_length=255)
    comment = models.TextField()
    published = models.DateTimeField()
    updated = models.DateTimeField()

    def __unicode__(self):
        return u'Video: {} Comment: {}'.format(self.video_id, self.comment)
