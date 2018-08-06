import logging

from dateutil import parser
from google.appengine.ext import deferred

from services import cloudnlp, youtube

logger = logging.getLogger(__name__)


def cloudnlp_analyze_transcript(video_pk):
    """
    Runs video transcripts through sentiment analysis.
    """
    from .models import Video  # avoid circular imports
    try:
        video = Video.objects.get(pk=video_pk)
    except Video.DoesNotExist:
        logger.info('Video %r no longer exists! Cant analyze!', video_pk)
        return
    if not video.transcript:
        logger.info(
            'Video %r does not have a transcript! Cant analyze!', video_pk)
        return
    try:
        client = cloudnlp.Client()
        analysis = client.analyze_sentiment(video.transcript)
    except Exception:
        logger.exception(
            'Error performing sentiment analysis on transcript for video %r',
            video.youtube_id)
        return
    video.analyzed_transcript = analysis
    video.sentiment = analysis['documentSentiment']['score']
    video.magnitude = analysis['documentSentiment']['magnitude']
    video.save()


def cloudnlp_analyze_comment(comment_pk):
    """
    Runs video comments through sentiment analysis.
    """
    from .models import VideoComment  # avoid circular imports
    try:
        comment = VideoComment.objects.get(pk=comment_pk)
    except VideoComment.DoesNotExist:
        logger.info(
            'Video comment %r no longer exists! Cant analyze!', comment_pk)
        return
    try:
        client = cloudnlp.Client()
        analysis = client.analyze_sentiment(comment.comment_raw)
    except Exception:
        logger.exception(
            'Error performing sentiment analysis on comment %r',
            comment.youtube_id)
        return
    comment.analyzed_comment = analysis
    comment.sentiment = analysis['documentSentiment']['score']
    comment.magnitude = analysis['documentSentiment']['magnitude']
    comment.save()


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
            comment = VideoComment.objects.create(
                video=video,
                youtube_id=c['snippet']['topLevelComment']['id'],
                author_display_name=data['authorDisplayName'],
                author_profile_image_url=data['authorProfileImageUrl'],
                comment_raw=data['textOriginal'],
                comment_rich=data['textDisplay'],
                published=published,
                updated=updated)
            deferred.defer(
                cloudnlp_analyze_comment, comment.pk, _queue='analyze')
    logger.info('Finished importing comment for video %r', video.youtube_id)


def youtube_import_transcript(video_pk):
    """
    Attempts to grab the transcript for the YouTube video.
    """
    from .models import Video
    try:
        video = Video.objects.get(pk=video_pk)
    except Video.DoesNotExist:
        logger.info('Video {} no longer exists! Cant import transcript')
        return
    try:
        client = youtube.Client()
        transcript = client.get_video_transcript(video.youtube_id)
    except Exception:
        logger.exception(
            'Error importing transcript for video %r', video.youtube_id)
        return
    if transcript:
        video.transcript = transcript
        video.save()
        deferred.defer(
            cloudnlp_analyze_transcript, video.pk, _queue='analyze')
