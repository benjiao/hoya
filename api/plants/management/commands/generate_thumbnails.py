from django.core.management.base import BaseCommand
from plants.models import PlantImage


class Command(BaseCommand):
    help = 'Generate WebP thumbnails for existing PlantImage records that lack one'

    def handle(self, *args, **options):
        qs = PlantImage.objects.filter(thumbnail='')
        total = qs.count()
        self.stdout.write(f'Processing {total} images...')
        ok = fail = 0
        for img in qs:
            try:
                img._generate_thumbnail()
                PlantImage.objects.filter(pk=img.pk).update(thumbnail=img.thumbnail.name)
                ok += 1
            except Exception as e:
                self.stderr.write(f'  FAILED pk={img.pk}: {e}')
                fail += 1
        self.stdout.write(f'Done: {ok} succeeded, {fail} failed.')
