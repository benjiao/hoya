from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plants', '0007_plantimage_taken_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='plant',
            name='watering_interval_days',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
