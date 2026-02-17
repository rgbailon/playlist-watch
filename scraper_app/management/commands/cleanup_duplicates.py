"""
Management command to clean up duplicate videos from database
"""
from django.core.management.base import BaseCommand
from scraper_app.models import Video
from django.db.models import Min


class Command(BaseCommand):
    help = 'Remove duplicate videos from the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Finding duplicate videos...')
        
        # Find duplicates by video_id
        duplicates = Video.objects.values('video_id').annotate(
            min_id=Min('id')
        ).filter(id__in=Video.objects.values('id'))
        
        deleted_count = 0
        
        for dup in duplicates:
            video_id = dup['video_id']
            min_id = dup['min_id']
            
            # Delete all except the one with minimum ID
            videos_to_delete = Video.objects.filter(video_id=video_id).exclude(id=min_id)
            count = videos_to_delete.count()
            
            if count > 0:
                videos_to_delete.delete()
                deleted_count += count
                self.stdout.write(f'  Removed {count} duplicates for video_id: {video_id}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully removed {deleted_count} duplicate videos'))
