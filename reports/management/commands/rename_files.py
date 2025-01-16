import os
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings
from core.models import Report, Room  


class Command(BaseCommand):
    help = "Sanitize and rename file paths for existing records in the database."

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting file renaming...")

        # Handle report images
        for report in Report.objects.all():
            if report.external_picture:
                old_path = os.path.join(settings.MEDIA_ROOT, report.external_picture.name)
                new_path = self.sanitize_file_path(old_path)

                if os.path.exists(old_path):
                    os.rename(old_path, new_path)  # Rename the file on disk
                    report.external_picture.name = os.path.relpath(new_path, settings.MEDIA_ROOT)
                    report.save()
                    self.stdout.write(f"Renamed: {old_path} -> {new_path}")

        # Handle room images
        for room in Room.objects.all():
            if room.room_picture:
                old_path = os.path.join(settings.MEDIA_ROOT, room.room_picture.name)
                new_path = self.sanitize_file_path(old_path)

                if os.path.exists(old_path):
                    os.rename(old_path, new_path)  # Rename the file on disk
                    room.room_picture.name = os.path.relpath(new_path, settings.MEDIA_ROOT)
                    room.save()
                    self.stdout.write(f"Renamed: {old_path} -> {new_path}")

        self.stdout.write("File renaming complete.")

    def sanitize_file_path(self, file_path):
        """Sanitize a file path by applying slugify to each component."""
        parts = file_path.split(os.sep)  # Split path into components
        sanitized_parts = [slugify(part) for part in parts]
        return os.sep.join(sanitized_parts)