import os

import cloudinary
import cloudinary.api
import cloudinary.uploader
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class CloudinaryMediaStorage(Storage):
    """Kitob rasmlarini Cloudinary'da saqlaydi (CLOUDINARY_URL orqali sozlanadi)."""

    def _public_id(self, name):
        # "books/rasm.jpg" -> "books/rasm" (Cloudinary kengaytmasiz saqlaydi)
        return os.path.splitext(name.replace("\\", "/"))[0]

    def _save(self, name, content):
        content.seek(0)
        result = cloudinary.uploader.upload(
            content,
            public_id=self._public_id(name),
            resource_type="image",
            overwrite=False,
        )
        return f"{result['public_id']}.{result['format']}"

    def exists(self, name):
        try:
            cloudinary.api.resource(self._public_id(name))
            return True
        except cloudinary.exceptions.NotFound:
            return False

    def delete(self, name):
        cloudinary.uploader.destroy(self._public_id(name), resource_type="image")

    def url(self, name):
        public_id, ext = os.path.splitext(name.replace("\\", "/"))
        return cloudinary.CloudinaryImage(public_id).build_url(
            format=ext.lstrip(".") or None,
            secure=True,
        )

    def size(self, name):
        return cloudinary.api.resource(self._public_id(name)).get("bytes", 0)
