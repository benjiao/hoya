from django.conf import settings
from config.celery import app
from .models import Plant, PlantCareLog


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
        intervals = [
            (logs[i].logged_at - logs[i + 1].logged_at).total_seconds() / 86400
            for i in range(len(logs) - 1)
        ]
        n = len(intervals)
        weights = list(range(n, 0, -1))  # most recent interval gets highest weight
        weighted = sum(w * iv for w, iv in zip(weights, intervals)) / sum(weights)
        Plant.objects.filter(pk=plant.pk).update(watering_interval_days=round(weighted, 2))
