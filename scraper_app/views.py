from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .services.scraper import (
    search_and_scrape_playlists,
    get_playlists,
    get_playlist_by_id,
    get_video_by_id,
)


def home(request):
    """Home page - show all playlists from JSON"""
    playlists = get_playlists()
    context = {"playlists": playlists}
    return render(request, "scraper_app/home.html", context)


@require_http_methods(["POST"])
def scrape_playlists(request):
    """Scrape playlists from YouTube"""
    query = request.POST.get("q", "").strip()

    if not query:
        messages.error(request, "Please enter a search query")
        return redirect("home")

    result = search_and_scrape_playlists(query, max_playlists=12)

    if result:
        messages.success(request, f"Found {result['total_playlists']} playlists!")
    else:
        messages.error(request, "No playlists found")

    return redirect("home")


def playlist_detail(request, playlist_id):
    """Display playlist details with videos from JSON"""
    playlist = get_playlist_by_id(playlist_id)

    if not playlist:
        from django.http import Http404

        raise Http404("Playlist not found")

    context = {"playlist": playlist}
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
