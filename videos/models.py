from django.db import models

from projects.models import Project


class Video(models.Model):
    """
    Represents a video within a project
    """
    project = models.ForeignKey(Project)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    # you tube specific data
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return u'{}'.format(self.name)
