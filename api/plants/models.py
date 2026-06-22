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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PlantImage(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='plants/images/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

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
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    notes = models.TextField(blank=True)
    logged_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plant.name} — {self.get_type_display()} on {self.logged_at:%Y-%m-%d}"
