from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plants', '0011_plantstatus_plant_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='plant',
            name='fertilizing_interval_days',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plantcarelog',
            name='type',
            field=models.CharField(
                blank=True,
                choices=[('watered', 'Watered'), ('repotted', 'Repotted'), ('fertilized', 'Fertilized')],
                default=None,
                max_length=20,
                null=True,
            ),
        ),
    ]
