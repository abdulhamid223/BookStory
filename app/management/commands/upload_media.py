import os

import cloudinary.uploader
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from app.models import Book


class Command(BaseCommand):
    help = "Lokal media/ papkasidagi kitob rasmlarini Cloudinary'ga yuklaydi"

    def handle(self, *args, **options):
        if not os.environ.get("CLOUDINARY_URL"):
            raise CommandError("CLOUDINARY_URL o'rnatilmagan")

        for book in Book.objects.exclude(image=""):
            path = settings.MEDIA_ROOT / book.image.name
            if not path.exists():
                self.stdout.write(self.style.WARNING(f"Topilmadi: {book.image.name}"))
                continue
            public_id = os.path.splitext(book.image.name)[0]
            cloudinary.uploader.upload(str(path), public_id=public_id, overwrite=True)
            self.stdout.write(self.style.SUCCESS(f"Yuklandi: {book.image.name}"))
