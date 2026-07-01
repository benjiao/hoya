from django.db import migrations


def add_periodic_task(apps, schema_editor):
    IntervalSchedule = apps.get_model('django_celery_beat', 'IntervalSchedule')
    PeriodicTask = apps.get_model('django_celery_beat', 'PeriodicTask')
    schedule, _ = IntervalSchedule.objects.get_or_create(every=1, period='hours')
    PeriodicTask.objects.get_or_create(
        name='compute_fertilizing_intervals',
        defaults={
            'interval': schedule,
            'task': 'plants.tasks.compute_fertilizing_intervals',
        },
    )


def remove_periodic_task(apps, schema_editor):
    PeriodicTask = apps.get_model('django_celery_beat', 'PeriodicTask')
    PeriodicTask.objects.filter(name='compute_fertilizing_intervals').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('plants', '0012_plant_fertilizing_interval_days_fertilized_type'),
        ('django_celery_beat', '0018_improve_crontab_helptext'),
    ]

    operations = [
        migrations.RunPython(add_periodic_task, remove_periodic_task),
    ]
