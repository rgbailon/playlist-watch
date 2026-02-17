from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Playlist, Video
from .services.scraper import (
    load_from_json,
    get_playlist_by_id,
    get_video_by_id,
)


def home(request):
    """Home page - show recent playlists from JSON"""
    recent_data = load_from_json()
    playlists = recent_data.get("playlists", []) if recent_data else []

    context = {
        "playlists": playlists,
        "recent_data": recent_data,
    }
    return render(request, "scraper_app/home.html", context)


def playlist_detail(request, playlist_id):
    """Display playlist details with all videos from JSON"""
    playlist = get_playlist_by_id(playlist_id)

    if not playlist:
        try:
            db_playlist = Playlist.objects.get(playlist_id=playlist_id)
            videos = db_playlist.videos.all()
            playlist = {
                "playlist_id": db_playlist.playlist_id,
                "title": db_playlist.title,
                "url": db_playlist.url,
                "video_count": db_playlist.video_count,
                "thumbnail": db_playlist.get_thumbnail(),
                "videos": [
                    {
                        "video_id": v.video_id,
                        "title": v.title,
                        "url": v.url,
                        "thumbnail": v.get_thumbnail(),
                        "position": v.position,
                    }
                    for v in videos
                ],
            }
        except Playlist.DoesNotExist:
            from django.http import Http404

            raise Http404("Playlist not found")

    context = {
        "playlist": playlist,
    }
    return render(request, "scraper_app/playlist_detail.html", context)


def video_player(request, video_id):
    """Video player page"""
    video, playlist = get_video_by_id(video_id)

    if not video:
        db_video = Video.objects.filter(video_id=video_id).first()
        if db_video:
            video = {
                "video_id": db_video.video_id,
                "title": db_video.title,
                "url": db_video.url,
                "thumbnail": db_video.get_thumbnail(),
            }
            playlist = {
                "playlist_id": db_video.playlist.playlist_id,
                "title": db_video.playlist.title,
            }
        else:
            from django.http import Http404

            raise Http404("Video not found")

    related_videos = []
    if playlist and "videos" in playlist:
        related_videos = [v for v in playlist["videos"] if v["video_id"] != video_id][
            :10
        ]

    context = {
        "video": video,
        "playlist": playlist,
        "related_videos": related_videos,
    }
    return render(request, "scraper_app/video_player.html", context)


def search_results(request):
    """Disabled - scraping not available"""
    return redirect("home")


@require_http_methods(["POST"])
def start_search(request):
    """Disabled - scraping not available"""
    return JsonResponse(
        {"success": False, "error": "Scraping not available on this deployment"}
    )


def get_search_results(request):
    """AJAX endpoint to get search results"""
    data = load_from_json()

    if not data:
        return JsonResponse({"success": False, "error": "No data available"})

    return JsonResponse({"success": True, "data": data})
