from django.conf import settings
from config.celery import app
from .models import Plant, PlantCareLog


def _compute_weighted_interval(logs):
    intervals = [
        (logs[i].logged_at - logs[i + 1].logged_at).total_seconds() / 86400
        for i in range(len(logs) - 1)
    ]
    n = len(intervals)
    weights = list(range(n, 0, -1))
    return round(sum(w * iv for w, iv in zip(weights, intervals)) / sum(weights), 2)


@app.task
def compute_watering_intervals(plant_pks=None):
    window = settings.WATERING_INTERVAL_WINDOW
    qs = Plant.objects.filter(pk__in=plant_pks) if plant_pks else Plant.objects.all()
    for plant in qs:
        logs = list(
            PlantCareLog.objects
            .filter(plant=plant, type=PlantCareLog.WATERED)
            .order_by('-logged_at')[:window]
        )
        if len(logs) < 2:
            continue
        Plant.objects.filter(pk=plant.pk).update(
            watering_interval_days=_compute_weighted_interval(logs)
        )


@app.task
def compute_fertilizing_intervals(plant_pks=None):
    window = settings.WATERING_INTERVAL_WINDOW
    qs = Plant.objects.filter(pk__in=plant_pks) if plant_pks else Plant.objects.all()
    for plant in qs:
        logs = list(
            PlantCareLog.objects
            .filter(plant=plant, type=PlantCareLog.FERTILIZED)
            .order_by('-logged_at')[:window]
        )
        if len(logs) < 2:
            continue
        Plant.objects.filter(pk=plant.pk).update(
            fertilizing_interval_days=_compute_weighted_interval(logs)
        )
