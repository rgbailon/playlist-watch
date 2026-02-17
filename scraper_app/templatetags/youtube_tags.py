import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def youtube_embed(video_url):
    if not video_url:
        return ""

    video_id = None
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, str(video_url))
        if match:
            video_id = match.group(1)
            break

    if video_id:
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        return mark_safe(
            f'<iframe width="100%" height="450" src="{embed_url}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>'
        )

    return ""

    video_id = None

    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
        r"youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, str(video_url))
        if match:
            video_id = match.group(1)
            break

    if video_id:
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        return mark_safe(
            f'<iframe width="100%" height="450" src="{embed_url}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>'
        )

    return ""
