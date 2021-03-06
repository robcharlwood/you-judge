from django.contrib.auth import get_user_model
from django.db import models


class Project(models.Model):
    """
    Tracks a specific field of interest or key event in time
    e.g Brexit or World Cup or Stars Wars - The last Jedi reviews
    """
    owner = models.ForeignKey(get_user_model())
    name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'{}'.format(self.name)

    class Meta:
        ordering = ['-created']
