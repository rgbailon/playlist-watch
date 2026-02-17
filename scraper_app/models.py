from django.db import models


class Playlist(models.Model):
    """Model to store YouTube playlist data"""
    playlist_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=200)
    url = models.URLField()
    video_count = models.CharField(max_length=50, default="N/A")
    thumbnail = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_thumbnail(self):
        """Get playlist thumbnail URL"""
        if self.thumbnail:
            return self.thumbnail
        # Default YouTube playlist thumbnail
        return f"https://img.youtube.com/vi/0/hqdefault.jpg"


class Video(models.Model):
    """Model to store YouTube video data"""
    playlist = models.ForeignKey(Playlist, related_name='videos', on_delete=models.CASCADE)
    video_id = models.CharField(max_length=50, db_index=True)
    title = models.CharField(max_length=300)
    url = models.URLField()
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['position']
    
    def __str__(self):
        return self.title
    
    def get_thumbnail(self):
        """Get video thumbnail URL"""
        return f"https://img.youtube.com/vi/{self.video_id}/hqdefault.jpg"
    
    def get_embed_url(self):
        """Get YouTube embed URL for player"""
        return f"https://www.youtube.com/embed/{self.video_id}"
    
    def get_piped_url(self):
        """Get Piped (alternative YouTube frontend) URL"""
        return f"https://piped.video/embed/{self.video_id}"
    
    def get_invidious_url(self):
        """Get Invidious (alternative YouTube frontend) URL"""
        return f"https://inv.tux.pizza/embed/{self.video_id}"
    
    def get_youtube_url(self):
        """Get direct YouTube watch URL"""
        return f"https://www.youtube.com/watch?v={self.video_id}"
