from django.contrib import admin
from .models import Playlist, Video


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['title', 'video_count', 'created_at']
    search_fields = ['title', 'playlist_id']
    list_filter = ['created_at']
    readonly_fields = ['created_at']


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'playlist', 'position', 'created_at']
    search_fields = ['title', 'video_id']
    list_filter = ['playlist', 'created_at']
    readonly_fields = ['created_at']
