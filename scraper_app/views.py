from django.shortcuts import render, redirect
from django.http import JsonResponse
from .services.scraper import (
    load_from_json,
    get_playlist_by_id,
    get_video_by_id,
)


def home(request):
    """Home page - show all playlists from JSON"""
    recent_data = load_from_json()
    playlists = recent_data.get("playlists", []) if recent_data else []

    context = {
        "playlists": playlists,
        "recent_data": recent_data,
    }
    return render(request, "scraper_app/home.html", context)


def search_results(request):
    """Search playlists from JSON data"""
    query = request.GET.get("q", "").lower().strip()

    recent_data = load_from_json()
    all_playlists = recent_data.get("playlists", []) if recent_data else []

    if query:
        filtered_playlists = [
            p for p in all_playlists if query in p.get("title", "").lower()
        ]
    else:
        filtered_playlists = all_playlists

    context = {
        "playlists": filtered_playlists,
        "query": query,
        "recent_data": recent_data,
    }
    return render(request, "scraper_app/home.html", context)


def playlist_detail(request, playlist_id):
    """Display playlist details from JSON"""
    playlist = get_playlist_by_id(playlist_id)

    if not playlist:
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
