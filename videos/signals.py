import logging

from google.appengine.ext import deferred

from .tasks import youtube_import_comments

logger = logging.getLogger(__name__)


def import_youtube_comments(sender, instance, created=None, **kwargs):
    """
    Imports YouTube comments for the passed video and stores them in the
    VideoComment model.
    """
    if created:
        logger.info('Retrieving comments for YouTube video %r', instance.pk)
        deferred.defer(youtube_import_comments, instance.pk, _queue='youtube')
