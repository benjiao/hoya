from django.db import migrations


def add_periodic_task(apps, schema_editor):
    IntervalSchedule = apps.get_model('django_celery_beat', 'IntervalSchedule')
    PeriodicTask = apps.get_model('django_celery_beat', 'PeriodicTask')
    schedule, _ = IntervalSchedule.objects.get_or_create(every=1, period='hours')
    PeriodicTask.objects.get_or_create(
        name='compute_watering_intervals',
        defaults={
            'interval': schedule,
            'task': 'plants.tasks.compute_watering_intervals',
        },
    )


def remove_periodic_task(apps, schema_editor):
    PeriodicTask = apps.get_model('django_celery_beat', 'PeriodicTask')
    PeriodicTask.objects.filter(name='compute_watering_intervals').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('plants', '0008_plant_watering_interval_days'),
        ('django_celery_beat', '0018_improve_crontab_helptext'),
    ]

    operations = [
        migrations.RunPython(add_periodic_task, remove_periodic_task),
    ]
