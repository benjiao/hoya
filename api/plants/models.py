import os
import re

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Location(models.Model):
    PATH_SEPARATOR = ' > '
    MAX_PATH_DEPTH = 50

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children'
    )
    skip_watering = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def path_names(self) -> list[str]:
        names = []
        seen = set()
        node = self
        depth = 0
        while node and depth < self.MAX_PATH_DEPTH:
            if node.pk in seen:
                break
            seen.add(node.pk)
            names.append(node.name)
            node = node.parent
            depth += 1
        return list(reversed(names))

    @property
    def display_name(self) -> str:
        return self.PATH_SEPARATOR.join(self.path_names)

    def __str__(self):
        return self.display_name

    def descendant_pks(self) -> set[int]:
        pks = {self.pk}
        frontier = [self.pk]
        while frontier:
            child_ids = list(
                Location.objects.filter(parent_id__in=frontier).values_list('pk', flat=True)
            )
            new_ids = [pk for pk in child_ids if pk not in pks]
            if not new_ids:
                break
            pks.update(new_ids)
            frontier = new_ids
        return pks


class Plant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plants')
    location = models.ForeignKey(
        Location, null=True, blank=True, on_delete=models.SET_NULL, related_name='plants'
    )
    name = models.CharField(max_length=255)
    scientific_name = models.CharField(max_length=255, blank=True)
    watering_interval_days = models.FloatField(null=True, blank=True)
    thumbnail_image = models.ForeignKey(
        'PlantImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


def _extract_exif_datetime(image_field):
    import io
    import datetime
    import logging
    try:
        from PIL import Image as PilImage
        data = image_field.read()
        image_field.seek(0)
        img = PilImage.open(io.BytesIO(data))
        exif = img.getexif()
        exif_ifd = exif.get_ifd(0x8769)  # ExifIFD sub-dict where DateTimeOriginal lives
        dt_str = (exif.get(36867) or exif.get(36868)
                  or exif_ifd.get(36867) or exif_ifd.get(36868))
        if dt_str:
            naive = datetime.datetime.strptime(dt_str, '%Y:%m:%d %H:%M:%S')
            return timezone.make_aware(naive)
    except Exception:
        logging.exception('EXIF extraction failed')
    return None


def plant_image_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    slug = re.sub(r'[^\w]+', '-', instance.plant.name).strip('-').lower()
    dt = timezone.now().strftime('%Y%m%dT%H%M%S')
    return f'plants/images/{slug}-{dt}{ext}'


def plant_thumbnail_upload_to(instance, filename):
    slug = re.sub(r'[^\w]+', '-', instance.plant.name).strip('-').lower()
    dt = timezone.now().strftime('%Y%m%dT%H%M%S')
    return f'plants/thumbnails/{slug}-{dt}.webp'


class PlantImage(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=plant_image_upload_to)
    thumbnail = models.ImageField(upload_to=plant_thumbnail_upload_to, blank=True)
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    taken_at = models.DateTimeField(null=True, blank=True)

    def _generate_thumbnail(self, size=300):
        import io
        from PIL import Image as PilImage, ImageOps
        from django.core.files.base import ContentFile

        self.image.seek(0)
        img = PilImage.open(io.BytesIO(self.image.read()))
        img = ImageOps.exif_transpose(img)
        img = img.convert('RGB')
        img.thumbnail((size, size), PilImage.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format='WEBP', quality=85)
        buf.seek(0)

        thumb_name = plant_thumbnail_upload_to(self, self.image.name)
        self.thumbnail.save(thumb_name, ContentFile(buf.read()), save=False)

    def save(self, *args, **kwargs):
        if not self.pk and self.taken_at is None:
            self.taken_at = _extract_exif_datetime(self.image) or timezone.now()
        is_new = not self.pk
        super().save(*args, **kwargs)
        if is_new and not self.thumbnail:
            try:
                self._generate_thumbnail()
                PlantImage.objects.filter(pk=self.pk).update(thumbnail=self.thumbnail.name)
            except Exception:
                import logging
                logging.exception('Thumbnail generation failed for PlantImage %s', self.pk)

    def __str__(self):
        return f"{self.plant.name} image {self.pk}"


class PlantCareLog(models.Model):
    WATERED = 'watered'
    REPOTTED = 'repotted'
    TYPE_CHOICES = [
        (WATERED, 'Watered'),
        (REPOTTED, 'Repotted'),
    ]

    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='care_logs')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, blank=True, null=True, default=None)
    notes = models.TextField(blank=True)
    logged_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        type_label = self.get_type_display() or 'Note'
        return f"{self.plant.name} — {type_label} on {self.logged_at:%Y-%m-%d}"
