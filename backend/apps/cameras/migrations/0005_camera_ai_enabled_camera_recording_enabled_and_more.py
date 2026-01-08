from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('cameras', '0004_remove_camera_name_unique'),
    ]

    operations = [
        migrations.AddField(
            model_name='camera',
            name='ai_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='camera',
            name='recording_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='camera',
            name='recording_retention_days',
            field=models.IntegerField(default=30),
        ),
        migrations.AddField(
            model_name='camera',
            name='roi_areas',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='camera',
            name='tripwires',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='camera',
            name='virtual_lines',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='camera',
            name='zone_triggers',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='camera',
            name='status',
            field=models.CharField(choices=[('online', 'Online'), ('offline', 'Offline')], default='online', max_length=10),
        ),
    ]
