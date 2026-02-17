from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Playlist, Video
from .services.scraper import (
    search_and_scrape_playlists,
    load_from_json,
    get_playlist_by_id,
    get_video_by_id,
)


def home(request):
    """Home page with search box"""
    query = request.GET.get("q", "")
    sort_by = request.GET.get("sort", "view_count")
    playlists = []
    error_message = None
    is_loading = False
    recent_data = None

    if query:
        existing_data = load_from_json()

        if existing_data and existing_data.get("search_query") == query:
            for pl_data in existing_data.get("playlists", []):
                playlists.append(pl_data)
        else:
            is_loading = True
    else:
        recent_data = load_from_json()

    context = {
        "query": query,
        "sort_by": sort_by,
        "playlists": playlists,
        "error_message": error_message,
        "is_loading": is_loading,
        "recent_data": recent_data,
    }
    return render(request, "scraper_app/home.html", context)


def search_results(request):
    """Perform search and save to JSON"""
    query = request.GET.get("q", "")
    sort_by = request.GET.get("sort", "view_count")

    if not query:
        return redirect("home")

    result = search_and_scrape_playlists(
        query, max_playlists=15, max_videos_per_playlist=50, sort_by=sort_by
    )

    if result:
        return redirect(f"/?q={query}&sort={sort_by}")
    else:
        return redirect("home")


def playlist_detail(request, playlist_id):
    """Display playlist details with all videos from JSON"""
    playlist = get_playlist_by_id(playlist_id)

    if not playlist:
        # Try to fetch from database as fallback
        db_playlist = get_object_or_404(Playlist, playlist_id=playlist_id)
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

    context = {
        "playlist": playlist,
    }
    return render(request, "scraper_app/playlist_detail.html", context)


def video_player(request, video_id):
    """Video player page"""
    video, playlist = get_video_by_id(video_id)

    if not video:
        # Try database fallback
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

    # Get related videos from same playlist
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


@require_http_methods(["POST"])
def start_search(request):
    """AJAX endpoint to start search"""
    query = request.POST.get("q", "")

    if not query:
        return JsonResponse({"success": False, "error": "No query provided"})

    try:
        # Start scraping in background
        result = search_and_scrape_playlists(
            query, max_playlists=10, max_videos_per_playlist=50
        )

        if result:
            return JsonResponse(
                {
                    "success": True,
                    "message": f"Scraped {result['total_playlists']} playlists",
                    "redirect": "/",
                }
            )
        else:
            return JsonResponse({"success": False, "error": "Scraping failed"})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


def get_search_results(request):
    """AJAX endpoint to get search results"""
    data = load_from_json()

    if not data:
        return JsonResponse({"success": False, "error": "No data available"})

    return JsonResponse({"success": True, "data": data})
