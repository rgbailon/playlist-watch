from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("scrape/", views.scrape_playlists, name="scrape"),
    path("playlist/<str:playlist_id>/", views.playlist_detail, name="playlist_detail"),
    path("video/<str:video_id>/", views.video_player, name="video_player"),
]
