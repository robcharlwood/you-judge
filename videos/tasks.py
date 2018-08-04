import logging

from dateutil import parser

from services import youtube

logger = logging.getLogger(__name__)


def youtube_import_comments(video_pk):
    """
    Task to import YouTube comments for a video
    """
    from .models import Video, VideoComment  # avoid circular imports
    try:
        video = Video.objects.get(pk=video_pk)
    except Video.DoesNotExist:
        logger.info('Video {} no longer exists! Cant import comments')
        return

    try:
        client = youtube.Client()
        comments = client.get_video_comments(video.youtube_id)
    except Exception:
        logger.exception(
            'Error importing comments for video %r', video.youtube_id)
        return
    if comments:
        for c in comments:
            data = c['snippet']['topLevelComment']['snippet']
            updated = parser.parse(data['updatedAt'])
            published = parser.parse(data['publishedAt'])
            VideoComment.objects.create(
                video=video,
                youtube_id=c['snippet']['topLevelComment']['id'],
                author_display_name=data['authorDisplayName'],
                author_profile_image_url=data['authorProfileImageUrl'],
                comment_raw=data['textOriginal'],
                comment_rich=data['textDisplay'],
                published=published,
                updated=updated)
    logger.info('Finished importing comment for video %r', video.youtube_id)
